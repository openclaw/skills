#!/usr/bin/env python3
"""
Merge multiple audio files into one.
"""

import argparse
import os
import subprocess
import sys
import tempfile

def merge_with_ffmpeg(files, output_file):
    """Merge audio files using ffmpeg concat."""
    # Create playlist file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for file in files:
            if not os.path.exists(file):
                print(f"Error: File not found: {file}")
                os.unlink(f.name)
                return False
            
            abs_path = os.path.abspath(file)
            f.write(f"file '{abs_path}'\n")
        playlist_file = f.name
    
    try:
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', playlist_file,
            '-c', 'copy', output_file,
            '-y'  # Overwrite output file
        ]
        
        print(f"Merging {len(files)} files into {output_file}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error merging audio: {result.stderr}")
            return False
        
        # Check output file size
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"Successfully created {output_file} ({size:,} bytes)")
            return True
        else:
            print("Error: Output file was not created")
            return False
            
    finally:
        os.unlink(playlist_file)

def merge_with_sox(files, output_file):
    """Merge audio files using sox (alternative method)."""
    try:
        cmd = ['sox'] + files + [output_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error merging with sox: {result.stderr}")
            return False
        
        return True
    except FileNotFoundError:
        print("Error: sox not installed. Install with 'brew install sox'")
        return False

def create_silence(duration_seconds, output_file):
    """Create a silent audio segment."""
    try:
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono',
            '-t', str(duration_seconds),
            '-c:a', 'libmp3lame',
            output_file,
            '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def merge_with_pauses(files, output_file, pause_duration=0):
    """Merge files with pauses between them."""
    if pause_duration <= 0:
        return merge_with_ffmpeg(files, output_file)
    
    # Create temporary files with pauses
    temp_files = []
    
    try:
        for i, file in enumerate(files):
            # Add the audio file
            temp_files.append(file)
            
            # Add pause after each file except the last
            if i < len(files) - 1 and pause_duration > 0:
                pause_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                pause_file.close()
                
                if create_silence(pause_duration, pause_file.name):
                    temp_files.append(pause_file.name)
                else:
                    print(f"Warning: Could not create pause segment")
        
        return merge_with_ffmpeg(temp_files, output_file)
    
    finally:
        # Clean up pause files
        for file in temp_files:
            if file not in files and os.path.exists(file):
                os.unlink(file)

def read_playlist(playlist_file):
    """Read files from playlist text file."""
    files = []
    try:
        with open(playlist_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('file '):
                    # ffmpeg concat format: file 'filename.mp3'
                    file_path = line[6:-1]  # Remove "file '" and trailing "'"
                    files.append(file_path)
                elif line and not line.startswith('#'):
                    # Simple format: one file per line
                    files.append(line)
        return files
    except Exception as e:
        print(f"Error reading playlist: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Merge multiple audio files')
    parser.add_argument('--files', nargs='+', help='Audio files to merge')
    parser.add_argument('--playlist', help='Playlist file containing list of audio files')
    parser.add_argument('--output', required=True, help='Output MP3 file path')
    parser.add_argument('--pause', type=float, default=0, help='Pause duration between files (seconds)')
    parser.add_argument('--method', choices=['ffmpeg', 'sox'], default='ffmpeg', help='Merge method')
    
    args = parser.parse_args()
    
    # Get list of files
    files = []
    
    if args.files:
        files = args.files
    elif args.playlist:
        files = read_playlist(args.playlist)
    else:
        parser.error("Either --files or --playlist is required")
    
    if not files:
        print("Error: No files to merge")
        sys.exit(1)
    
    # Check if all files exist
    missing_files = [f for f in files if not os.path.exists(f)]
    if missing_files:
        print("Error: The following files were not found:")
        for f in missing_files:
            print(f"  {f}")
        sys.exit(1)
    
    print(f"Merging {len(files)} files:")
    for i, file in enumerate(files, 1):
        size = os.path.getsize(file)
        print(f"  {i:2d}. {file} ({size:,} bytes)")
    
    # Merge files
    success = False
    
    if args.method == 'ffmpeg':
        if args.pause > 0:
            success = merge_with_pauses(files, args.output, args.pause)
        else:
            success = merge_with_ffmpeg(files, args.output)
    elif args.method == 'sox':
        success = merge_with_sox(files, args.output)
    
    if success:
        print(f"Successfully created: {args.output}")
    else:
        print("Failed to merge audio files")
        sys.exit(1)

if __name__ == '__main__':
    main()
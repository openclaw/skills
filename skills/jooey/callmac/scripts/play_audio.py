#!/usr/bin/env python3
"""
Audio playback control utilities.
"""

import argparse
import os
import subprocess
import sys
import signal
import time

# Global variable to track playback process
playback_process = None

def signal_handler(sig, frame):
    """Handle interrupt signals."""
    global playback_process
    if playback_process:
        print("\nStopping playback...")
        playback_process.terminate()
        playback_process.wait()
    sys.exit(0)

def play_audio_file(file_path, loops=1, volume=None):
    """Play audio file using afplay."""
    global playback_process
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    if volume is not None:
        # Set system volume
        volume_cmd = ['osascript', '-e', f'set volume output volume {volume}']
        subprocess.run(volume_cmd, capture_output=True)
    
    for i in range(loops):
        if loops > 1:
            print(f"Playing loop {i+1}/{loops}")
        
        try:
            playback_process = subprocess.Popen(['afplay', file_path])
            playback_process.wait()
        except KeyboardInterrupt:
            if playback_process:
                playback_process.terminate()
            return False
        except Exception as e:
            print(f"Error playing audio: {e}")
            return False
    
    return True

def stop_playback():
    """Stop all audio playback."""
    # Kill afplay processes
    subprocess.run(['pkill', '-f', 'afplay'], capture_output=True)
    print("Stopped all audio playback")
    return True

def get_system_volume():
    """Get current system volume."""
    try:
        result = subprocess.run(
            ['osascript', '-e', 'output volume of (get volume settings)'],
            capture_output=True,
            text=True
        )
        return int(result.stdout.strip())
    except:
        return None

def get_mute_status():
    """Get current mute status."""
    try:
        result = subprocess.run(
            ['osascript', '-e', 'output muted of (get volume settings)'],
            capture_output=True,
            text=True
        )
        return result.stdout.strip().lower() == 'true'
    except:
        return None

def set_system_volume(volume):
    """Set system volume (0-100)."""
    try:
        volume = max(0, min(100, volume))
        cmd = ['osascript', '-e', f'set volume output volume {volume}']
        subprocess.run(cmd, capture_output=True)
        print(f"Volume set to {volume}%")
        return True
    except Exception as e:
        print(f"Error setting volume: {e}")
        return False

def set_mute_status(mute):
    """Set mute status."""
    try:
        if mute:
            cmd = ['osascript', '-e', 'set volume with output muted']
        else:
            cmd = ['osascript', '-e', 'set volume without output muted']
        
        subprocess.run(cmd, capture_output=True)
        status = "muted" if mute else "unmuted"
        print(f"System {status}")
        return True
    except Exception as e:
        print(f"Error setting mute: {e}")
        return False

def list_audio_files(directory='.'):
    """List audio files in directory."""
    audio_extensions = {'.mp3', '.wav', '.aiff', '.aif', '.m4a', '.flac'}
    
    files = []
    for file in os.listdir(directory):
        if os.path.isfile(file) and os.path.splitext(file)[1].lower() in audio_extensions:
            files.append(file)
    
    return sorted(files)

def main():
    parser = argparse.ArgumentParser(description='Audio playback control')
    parser.add_argument('--file', help='Audio file to play')
    parser.add_argument('--loops', type=int, default=1, help='Number of times to play')
    parser.add_argument('--volume', type=int, help='Playback volume 0-100')
    parser.add_argument('--stop', action='store_true', help='Stop all audio playback')
    parser.add_argument('--get-volume', action='store_true', help='Get current system volume')
    parser.add_argument('--set-volume', type=int, help='Set system volume (0-100)')
    parser.add_argument('--mute', action='store_true', help='Mute system audio')
    parser.add_argument('--unmute', action='store_true', help='Unmute system audio')
    parser.add_argument('--list', action='store_true', help='List audio files in current directory')
    parser.add_argument('--delay', type=float, default=0, help='Delay before playback (seconds)')
    
    args = parser.parse_args()
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Handle stop command
    if args.stop:
        stop_playback()
        return
    
    # Handle volume commands
    if args.get_volume:
        volume = get_system_volume()
        mute = get_mute_status()
        if volume is not None:
            mute_status = " (muted)" if mute else ""
            print(f"System volume: {volume}%{mute_status}")
        return
    
    if args.set_volume is not None:
        set_system_volume(args.set_volume)
        return
    
    if args.mute:
        set_mute_status(True)
        return
    
    if args.unmute:
        set_mute_status(False)
        return
    
    # Handle list command
    if args.list:
        files = list_audio_files()
        if files:
            print("Audio files in current directory:")
            for file in files:
                print(f"  {file}")
        else:
            print("No audio files found")
        return
    
    # Handle playback
    if not args.file:
        parser.error("--file is required for playback")
    
    # Add delay if specified
    if args.delay > 0:
        print(f"Waiting {args.delay} seconds before playback...")
        time.sleep(args.delay)
    
    # Play audio
    success = play_audio_file(args.file, args.loops, args.volume)
    
    if success:
        print("Playback completed")
    else:
        print("Playback failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
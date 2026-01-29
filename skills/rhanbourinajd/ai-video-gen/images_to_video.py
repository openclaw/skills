#!/usr/bin/env python3
"""
Convert image sequence to video using FFmpeg
"""

import argparse
import subprocess
import sys
from pathlib import Path


def images_to_video(image_files, output_path, fps=24, quality='high'):
    """Convert list of images to video"""
    
    # Quality presets
    crf_values = {
        'low': 28,
        'medium': 23,
        'high': 18,
        'ultra': 15
    }
    crf = crf_values.get(quality, 18)
    
    print(f"🎬 Creating video from {len(image_files)} images at {fps} fps...")
    
    # Create temporary file list
    file_list_path = Path('filelist.txt')
    with open(file_list_path, 'w') as f:
        for img in image_files:
            duration = 1.0 / fps
            f.write(f"file '{Path(img).absolute()}'\n")
            f.write(f"duration {duration}\n")
    
    # FFmpeg command
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(file_list_path),
        '-vsync', 'vfr',
        '-pix_fmt', 'yuv420p',
        '-crf', str(crf),
        output_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Video created: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e.stderr}")
        sys.exit(1)
    finally:
        # Clean up temp file
        if file_list_path.exists():
            file_list_path.unlink()


def main():
    parser = argparse.ArgumentParser(description='Convert images to video')
    parser.add_argument('--images', nargs='+', required=True, help='Input image files')
    parser.add_argument('--output', default='output.mp4', help='Output video file')
    parser.add_argument('--fps', type=int, default=24, help='Frames per second')
    parser.add_argument('--quality', choices=['low', 'medium', 'high', 'ultra'], 
                       default='high', help='Output quality')
    
    args = parser.parse_args()
    
    # Validate images exist
    for img in args.images:
        if not Path(img).exists():
            print(f"❌ Error: Image not found: {img}")
            sys.exit(1)
    
    images_to_video(args.images, args.output, args.fps, args.quality)


if __name__ == '__main__':
    main()

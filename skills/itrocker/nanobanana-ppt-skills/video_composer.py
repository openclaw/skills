#!/usr/bin/env python3
"""
FFmpeg Video Composer Module.

Responsible for converting static images to videos, concatenating video clips,
and composing complete PPT videos.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional


# =============================================================================
# Constants
# =============================================================================

DEFAULT_RESOLUTION = "1920x1080"
DEFAULT_FPS = 24
DEFAULT_SLIDE_DURATION = 2
FFMPEG_TIMEOUT = 300  # 5 minutes


# =============================================================================
# Exceptions
# =============================================================================

class FFmpegError(Exception):
    """Exception for FFmpeg-related errors."""
    pass


# =============================================================================
# Video Composer
# =============================================================================

class VideoComposer:
    """FFmpeg-based video composer for PPT video generation."""

    def __init__(self, ffmpeg_path: str = "ffmpeg") -> None:
        """
        Initialize video composer.

        Args:
            ffmpeg_path: Path to FFmpeg executable.

        Raises:
            FFmpegError: If FFmpeg is not available.
        """
        self.ffmpeg_path = ffmpeg_path
        self._verify_ffmpeg()

    def _verify_ffmpeg(self) -> None:
        """Verify FFmpeg is available and working."""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                version = result.stdout.split("\n")[0]
                print(f"FFmpeg ready: {version}")
            else:
                raise FFmpegError("FFmpeg version check failed")
        except FileNotFoundError:
            raise FFmpegError(
                "FFmpeg not found.\n"
                "Please install FFmpeg: brew install ffmpeg"
            )
        except subprocess.TimeoutExpired:
            raise FFmpegError("FFmpeg version check timed out")

    # -------------------------------------------------------------------------
    # FFmpeg Execution
    # -------------------------------------------------------------------------

    def _run_ffmpeg(
        self,
        cmd: List[str],
        description: str = "",
    ) -> bool:
        """
        Execute FFmpeg command.

        Args:
            cmd: FFmpeg command as list of arguments.
            description: Operation description for logging.

        Returns:
            True if successful, False otherwise.
        """
        if description:
            print(f"  {description}...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=FFMPEG_TIMEOUT,
            )

            if result.returncode != 0:
                print(f"  FFmpeg failed: {result.stderr[:200]}")
                return False

            if description:
                print(f"  {description} complete")
            return True

        except subprocess.TimeoutExpired:
            print("  FFmpeg timed out")
            return False
        except Exception as e:
            print(f"  FFmpeg error: {e}")
            return False

    # -------------------------------------------------------------------------
    # Static Video Creation
    # -------------------------------------------------------------------------

    def create_static_video(
        self,
        image_path: str,
        duration: int = DEFAULT_SLIDE_DURATION,
        output_path: Optional[str] = None,
        resolution: str = DEFAULT_RESOLUTION,
        fps: int = DEFAULT_FPS,
    ) -> Optional[str]:
        """
        Convert static image to video.

        Args:
            image_path: Path to source image.
            duration: Video duration in seconds.
            output_path: Output video path (auto-generated if not provided).
            resolution: Target resolution (WxH format).
            fps: Target frame rate.

        Returns:
            Path to output video, or None if failed.
        """
        if not os.path.exists(image_path):
            print(f"  Image not found: {image_path}")
            return None

        # Auto-generate output path
        if not output_path:
            stem = Path(image_path).stem
            output_path = str(Path(image_path).parent / f"{stem}_static.mp4")

        width, height = resolution.split("x")

        # Build FFmpeg command
        cmd = [
            self.ffmpeg_path,
            "-y",  # Overwrite output
            "-loop", "1",  # Loop input image
            "-i", image_path,
            "-c:v", "libx264",  # H.264 codec
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-vf", (
                f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1"
            ),
            "-r", str(fps),
            output_path,
        ]

        description = f"Image to video ({Path(image_path).name}, {duration}s)"
        success = self._run_ffmpeg(cmd, description)

        return output_path if success else None

    # -------------------------------------------------------------------------
    # Video Concatenation
    # -------------------------------------------------------------------------

    def concat_videos(
        self,
        video_list: List[str],
        output_path: str,
        normalize_params: bool = True,
        target_resolution: str = DEFAULT_RESOLUTION,
        target_fps: int = DEFAULT_FPS,
    ) -> bool:
        """
        Concatenate multiple videos into one.

        Args:
            video_list: List of video paths in order.
            output_path: Output video path.
            normalize_params: Whether to normalize video parameters.
            target_resolution: Target resolution for normalization.
            target_fps: Target FPS for normalization.

        Returns:
            True if successful, False otherwise.
        """
        if not video_list:
            print("  Empty video list")
            return False

        # Verify all videos exist
        for video_path in video_list:
            if not os.path.exists(video_path):
                print(f"  Video not found: {video_path}")
                return False

        if normalize_params:
            return self._concat_with_filter(
                video_list, output_path, target_resolution, target_fps
            )
        else:
            return self._concat_with_demuxer(video_list, output_path)

    def _concat_with_demuxer(
        self,
        video_list: List[str],
        output_path: str,
    ) -> bool:
        """
        Concatenate videos using concat demuxer (fast, no re-encoding).

        Args:
            video_list: List of video paths.
            output_path: Output video path.

        Returns:
            True if successful, False otherwise.
        """
        # Create temporary file list
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            concat_file = f.name
            for video_path in video_list:
                f.write(f"file '{os.path.abspath(video_path)}'\n")

        try:
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                output_path,
            ]

            description = f"Concatenating {len(video_list)} videos (fast mode)"
            return self._run_ffmpeg(cmd, description)
        finally:
            if os.path.exists(concat_file):
                os.remove(concat_file)

    def _concat_with_filter(
        self,
        video_list: List[str],
        output_path: str,
        resolution: str,
        fps: int,
    ) -> bool:
        """
        Concatenate videos using filter_complex (re-encodes, normalizes parameters).

        Args:
            video_list: List of video paths.
            output_path: Output video path.
            resolution: Target resolution.
            fps: Target FPS.

        Returns:
            True if successful, False otherwise.
        """
        width, height = resolution.split("x")

        # Build input arguments
        inputs = []
        for video_path in video_list:
            inputs.extend(["-i", video_path])

        # Build filter for each input
        filter_parts = []
        for i in range(len(video_list)):
            filter_parts.append(
                f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,"
                f"fps={fps}[v{i}]"
            )

        # Build concat filter
        concat_inputs = "".join(f"[v{i}]" for i in range(len(video_list)))
        filter_complex = (
            ";".join(filter_parts) + ";"
            f"{concat_inputs}concat=n={len(video_list)}:v=1:a=0[outv]"
        )

        cmd = [
            self.ffmpeg_path,
            "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            output_path,
        ]

        description = f"Concatenating {len(video_list)} videos (normalized)"
        return self._run_ffmpeg(cmd, description)

    # -------------------------------------------------------------------------
    # Full PPT Video Composition
    # -------------------------------------------------------------------------

    def compose_full_ppt_video(
        self,
        slides_paths: List[str],
        transitions_dict: Dict[str, str],
        output_path: str,
        slide_duration: int = DEFAULT_SLIDE_DURATION,
        include_preview: bool = False,
        preview_video_path: Optional[str] = None,
        resolution: str = DEFAULT_RESOLUTION,
        fps: int = DEFAULT_FPS,
    ) -> bool:
        """
        Compose complete PPT video from slides and transitions.

        Video structure:
        1. [Optional] Preview video
        2. Transition 1-2
        3. Slide 2 static (N seconds)
        4. Transition 2-3
        5. Slide 3 static (N seconds)
        ...

        Args:
            slides_paths: List of slide image paths.
            transitions_dict: Dict mapping 'from-to' keys to transition video paths.
            output_path: Output video path.
            slide_duration: Duration for each static slide.
            include_preview: Whether to include preview video.
            preview_video_path: Path to preview video.
            resolution: Target resolution.
            fps: Target FPS.

        Returns:
            True if successful, False otherwise.
        """
        print("\n" + "=" * 80)
        print("Composing Full PPT Video")
        print("=" * 80)

        num_slides = len(slides_paths)
        print(f"\nParameters:")
        print(f"  Slides: {num_slides}")
        print(f"  Duration per slide: {slide_duration}s")
        print(f"  Include preview: {'Yes' if include_preview else 'No'}")
        print(f"  Resolution: {resolution}")
        print(f"  FPS: {fps}\n")

        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="ppt_video_")
        print(f"Temp directory: {temp_dir}\n")

        try:
            # Generate static videos (skip first slide)
            print("Generating static video clips...")
            static_videos = {}

            for i in range(1, num_slides):
                slide_path = slides_paths[i]
                slide_num = Path(slide_path).stem.split("-")[-1]

                static_path = os.path.join(temp_dir, f"slide-{slide_num}-static.mp4")
                result = self.create_static_video(
                    image_path=slide_path,
                    duration=slide_duration,
                    output_path=static_path,
                    resolution=resolution,
                    fps=fps,
                )

                if not result:
                    print(f"  Failed to create static video for slide {slide_num}")
                    return False

                static_videos[slide_num] = static_path

            print(f"  Generated {len(static_videos)} static videos\n")

            # Build video sequence
            print("Building video sequence...")
            video_sequence = []

            # Optional preview
            if include_preview and preview_video_path and os.path.exists(preview_video_path):
                video_sequence.append(preview_video_path)
                print("  + Preview video")

            # Add transitions and static videos
            for i in range(num_slides - 1):
                from_num = Path(slides_paths[i]).stem.split("-")[-1]
                to_num = Path(slides_paths[i + 1]).stem.split("-")[-1]
                transition_key = f"{from_num}-{to_num}"

                # Add transition video
                if transition_key in transitions_dict:
                    transition_path = transitions_dict[transition_key]
                    if os.path.exists(transition_path):
                        video_sequence.append(transition_path)
                        print(f"  + Transition {transition_key}")
                    else:
                        print(f"  ! Transition missing: {transition_key}")
                else:
                    print(f"  ! Transition not defined: {transition_key}")

                # Add target slide static video
                if to_num in static_videos:
                    video_sequence.append(static_videos[to_num])
                    print(f"  + Static slide-{to_num} ({slide_duration}s)")

            print(f"\n  Total clips: {len(video_sequence)}\n")

            if not video_sequence:
                print("  No video clips to concatenate")
                return False

            # Concatenate all videos
            print("Concatenating videos...")
            success = self.concat_videos(
                video_list=video_sequence,
                output_path=output_path,
                normalize_params=True,
                target_resolution=resolution,
                target_fps=fps,
            )

            if success:
                file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print("\n" + "=" * 80)
                print("Full PPT Video Complete!")
                print("=" * 80)
                print(f"  Output: {output_path}")
                print(f"  Size: {file_size_mb:.2f} MB")
                print(f"  Clips: {len(video_sequence)}")
                print("=" * 80 + "\n")
            else:
                print("\n  Video concatenation failed")

            return success

        finally:
            # Cleanup
            print("Cleaning up temp files...")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                print(f"  Removed: {temp_dir}\n")


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == "__main__":
    composer = VideoComposer()

    # Test: Image to video
    test_image = "outputs/20260109_121822/images/slide-02.png"
    if os.path.exists(test_image):
        print("\nTest: Image to static video")
        result = composer.create_static_video(
            image_path=test_image,
            duration=3,
            output_path="test_outputs/test_static.mp4",
        )
        if result:
            print(f"  Test passed: {result}")
        else:
            print("  Test failed")
    else:
        print(f"Skipping test: Image not found {test_image}")

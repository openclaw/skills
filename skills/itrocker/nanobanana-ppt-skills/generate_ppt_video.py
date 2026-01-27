#!/usr/bin/env python3
"""
PPT Video Generator - Generate videos with transitions from PPT slide images.

This script integrates image processing, video material generation, and video
composition to create complete PPT presentation videos.
"""

import argparse
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from video_composer import VideoComposer
from video_materials import VideoMaterialsGenerator


# =============================================================================
# Constants
# =============================================================================

DEFAULT_VIDEO_MODE = "both"
DEFAULT_VIDEO_DURATION = "5"
DEFAULT_SLIDE_DURATION = 5
DEFAULT_VIDEO_QUALITY = "pro"
DEFAULT_MAX_CONCURRENT = 3


# =============================================================================
# Video Generation
# =============================================================================

def scan_slide_images(slides_dir: str) -> List[str]:
    """
    Scan directory for PPT slide images.

    Args:
        slides_dir: Directory containing slide images.

    Returns:
        Sorted list of slide image paths.

    Raises:
        FileNotFoundError: If no slide images are found.
    """
    slides_paths = sorted(Path(slides_dir).glob("slide-*.png"))

    if not slides_paths:
        raise FileNotFoundError(
            f"No PPT images found in {slides_dir} (expected format: slide-*.png)"
        )

    return [str(p) for p in slides_paths]


def create_output_directories(output_dir: str) -> str:
    """
    Create output directory structure.

    Args:
        output_dir: Base output directory.

    Returns:
        Path to videos subdirectory.
    """
    os.makedirs(output_dir, exist_ok=True)
    videos_dir = os.path.join(output_dir, "videos")
    os.makedirs(videos_dir, exist_ok=True)
    return videos_dir


def generate_ppt_video_from_images(
    slides_dir: str,
    output_dir: str,
    video_mode: str = DEFAULT_VIDEO_MODE,
    video_duration: str = DEFAULT_VIDEO_DURATION,
    slide_duration: int = DEFAULT_SLIDE_DURATION,
    video_quality: str = DEFAULT_VIDEO_QUALITY,
    max_concurrent: int = DEFAULT_MAX_CONCURRENT,
    skip_preview: bool = False,
    prompts_file: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Generate video from existing PPT images.

    Args:
        slides_dir: Directory containing PPT slide images.
        output_dir: Output directory for generated videos.
        video_mode: Output mode - both/local/web.
        video_duration: Transition video duration (5 or 10 seconds).
        slide_duration: Duration for each slide (seconds).
        video_quality: Video quality (std/pro).
        max_concurrent: Maximum concurrent video generation tasks.
        skip_preview: Whether to skip preview video generation.
        prompts_file: Path to transition prompts JSON file.

    Returns:
        Result dictionary with generation statistics, or None on failure.
    """
    print("\n" + "=" * 80)
    print("PPT Video Generation - Full Pipeline")
    print("=" * 80)

    # Phase 1: Scan slide images
    print(f"\nScanning slides directory: {slides_dir}")
    try:
        slides_paths = scan_slide_images(slides_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None

    num_slides = len(slides_paths)
    print(f"Found {num_slides} slides:")
    for i, path in enumerate(slides_paths, 1):
        print(f"  {i}. {Path(path).name}")

    # Phase 2: Create output directories
    videos_dir = create_output_directories(output_dir)
    print(f"\nOutput directory: {output_dir}")
    print(f"  Videos: {videos_dir}/")

    # Phase 3: Generate video materials
    print("\n" + "=" * 80)
    print("Phase 1: Generate Video Materials (Preview + Transitions)")
    print("=" * 80)

    materials_generator = VideoMaterialsGenerator(
        max_concurrent=max_concurrent,
        prompts_file=prompts_file,
    )

    # Prepare content contexts
    content_contexts = [
        f"Transition from slide {i+1} to slide {i+2}"
        for i in range(num_slides - 1)
    ]

    materials_result = materials_generator.generate_all_materials(
        slides_paths=slides_paths,
        output_dir=videos_dir,
        content_contexts=content_contexts,
        duration=video_duration,
        mode=video_quality,
        skip_preview=skip_preview,
    )

    if materials_result["failed_count"] > 0:
        print(f"\nWarning: {materials_result['failed_count']} video(s) failed")
        print("Continuing with composition, final video may be incomplete...")

    # Phase 4: Compose full video (if needed)
    if video_mode in ("both", "local"):
        print("\n" + "=" * 80)
        print("Phase 2: Compose Full PPT Video")
        print("=" * 80)

        composer = VideoComposer()

        # Build transitions dictionary
        transitions_dict = {
            key: result["video_path"]
            for key, result in materials_result["transitions"].items()
            if result["success"]
        }

        full_video_path = os.path.join(output_dir, "full_ppt_video.mp4")

        preview_video = None
        if materials_result["preview"] and not skip_preview:
            preview_video = materials_result["preview"]["video_path"]

        compose_success = composer.compose_full_ppt_video(
            slides_paths=slides_paths,
            transitions_dict=transitions_dict,
            output_path=full_video_path,
            slide_duration=slide_duration,
            include_preview=False,
            preview_video_path=preview_video,
        )

        if compose_success:
            print(f"Full video generated: {full_video_path}")
        else:
            print("Full video composition failed")

    # Phase 5: Generate web viewer (if needed)
    if video_mode in ("both", "web"):
        print("\n" + "=" * 80)
        print("Phase 3: Generate Web Viewer")
        print("=" * 80)

        generate_video_viewer(
            slides_paths=slides_paths,
            transitions_result=materials_result["transitions"],
            preview_result=materials_result.get("preview"),
            output_dir=output_dir,
        )

    # Phase 6: Print summary
    print("\n" + "=" * 80)
    print("PPT Video Generation Complete!")
    print("=" * 80)

    print(f"\nStatistics:")
    print(f"  Slides: {num_slides}")
    print(f"  Videos: {materials_result['success_count']} success, "
          f"{materials_result['failed_count']} failed")
    total_minutes = materials_result["total_duration"] / 60
    print(f"  Duration: {materials_result['total_duration']}s ({total_minutes:.1f}m)")

    print(f"\nOutput files:")
    if video_mode in ("both", "local"):
        print(f"  Full video: {output_dir}/full_ppt_video.mp4")
    if video_mode in ("both", "web"):
        print(f"  Web viewer: {output_dir}/video_index.html")
    print(f"  Video materials: {videos_dir}/")
    print(f"  Metadata: {videos_dir}/video_metadata.json")

    print("\n" + "=" * 80 + "\n")

    return {
        "output_dir": output_dir,
        "num_slides": num_slides,
        "materials_result": materials_result,
        "video_mode": video_mode,
    }


# =============================================================================
# Web Viewer Generation
# =============================================================================

def generate_video_viewer(
    slides_paths: List[str],
    transitions_result: Dict[str, Any],
    preview_result: Optional[Dict[str, Any]],
    output_dir: str,
) -> Optional[str]:
    """
    Generate HTML video viewer.

    Args:
        slides_paths: List of slide image paths.
        transitions_result: Transition video generation results.
        preview_result: Preview video generation result.
        output_dir: Output directory.

    Returns:
        Path to generated HTML file, or None if template not found.
    """
    print("Generating web viewer...")

    template_path = "templates/video_viewer.html"
    output_html = os.path.join(output_dir, "video_index.html")

    if not os.path.exists(template_path):
        print(f"Warning: Template not found: {template_path}, skipping web viewer")
        return None

    # Build slides data (relative paths)
    slides_data = [os.path.relpath(path, output_dir) for path in slides_paths]

    # Build transitions data
    transitions_data = {
        key: os.path.relpath(result["video_path"], output_dir)
        for key, result in transitions_result.items()
        if result["success"]
    }

    # Build preview data
    preview_data = None
    if preview_result:
        preview_data = os.path.relpath(preview_result["video_path"], output_dir)

    # Read template and replace placeholders
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    replacements = [
        ("/* SLIDES_DATA_PLACEHOLDER */", json.dumps(slides_data, ensure_ascii=False)),
        ("/* TRANSITIONS_DATA_PLACEHOLDER */", json.dumps(transitions_data, ensure_ascii=False)),
        ("/* PREVIEW_DATA_PLACEHOLDER */", json.dumps(preview_data, ensure_ascii=False) if preview_data else "null"),
    ]

    for placeholder, value in replacements:
        html_content = html_content.replace(placeholder, value)

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Web viewer generated: {output_html}")
    return output_html


# =============================================================================
# Command Line Interface
# =============================================================================

def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="PPT Video Generator - Create videos with transitions from PPT images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with prompts file
  python generate_ppt_video.py \\
    --slides-dir outputs/xxx/images \\
    --output-dir outputs/xxx_video \\
    --prompts-file outputs/xxx/transition_prompts.json

  # Full parameters
  python generate_ppt_video.py \\
    --slides-dir outputs/xxx/images \\
    --output-dir outputs/xxx_video \\
    --prompts-file outputs/xxx/transition_prompts.json \\
    --video-mode both \\
    --video-duration 5 \\
    --slide-duration 5 \\
    --video-quality pro \\
    --max-concurrent 3

Workflow:
  1. Generate PPT images: python generate_ppt.py ...
  2. Have Claude Code analyze images and generate prompts:
     Run in Claude Code: "Analyze images in outputs/xxx/images, generate transition prompts"
  3. Generate videos: python generate_ppt_video.py --prompts-file ...

Notes:
  - Ensure KLING_ACCESS_KEY and KLING_SECRET_KEY are configured in .env
  - Claude Code must analyze images to create transition_prompts.json
  - First-last frame videos require pro mode (high quality)
  - Kling API has concurrent limit of 3, generation takes time
""",
    )

    parser.add_argument(
        "--slides-dir",
        required=True,
        help="PPT images directory (containing slide-01.png, slide-02.png, etc.)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory",
    )
    parser.add_argument(
        "--video-mode",
        choices=["both", "local", "web"],
        default=DEFAULT_VIDEO_MODE,
        help=f"Output mode: both/local/web (default: {DEFAULT_VIDEO_MODE})",
    )
    parser.add_argument(
        "--video-duration",
        choices=["5", "10"],
        default=DEFAULT_VIDEO_DURATION,
        help=f"Transition video duration in seconds (default: {DEFAULT_VIDEO_DURATION})",
    )
    parser.add_argument(
        "--slide-duration",
        type=int,
        default=DEFAULT_SLIDE_DURATION,
        help=f"Duration per slide in seconds (default: {DEFAULT_SLIDE_DURATION})",
    )
    parser.add_argument(
        "--video-quality",
        choices=["std", "pro"],
        default=DEFAULT_VIDEO_QUALITY,
        help=f"Video quality: std/pro (default: {DEFAULT_VIDEO_QUALITY})",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=DEFAULT_MAX_CONCURRENT,
        help=f"Maximum concurrent tasks (default: {DEFAULT_MAX_CONCURRENT})",
    )
    parser.add_argument(
        "--skip-preview",
        action="store_true",
        help="Skip preview video generation",
    )
    parser.add_argument(
        "--prompts-file",
        required=True,
        help="Path to transition prompts JSON file (generated by Claude Code)",
    )

    return parser


def validate_inputs(args: argparse.Namespace) -> bool:
    """
    Validate command line inputs.

    Args:
        args: Parsed command line arguments.

    Returns:
        True if all inputs are valid, False otherwise.
    """
    if not os.path.exists(args.slides_dir):
        print(f"Error: Slides directory not found: {args.slides_dir}")
        return False

    if not os.path.exists(args.prompts_file):
        print(f"Error: Prompts file not found: {args.prompts_file}")
        print(f"\nHow to generate prompts file:")
        print(f"  1. Run in Claude Code:")
        print(f"     'Analyze images in {args.slides_dir}, generate transition prompts,")
        print(f"      save to transition_prompts.json'")
        print(f"  2. Use --prompts-file to specify the generated file path")
        return False

    return True


def main() -> None:
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args()

    # Validate inputs
    if not validate_inputs(args):
        sys.exit(1)

    # Execute generation
    try:
        result = generate_ppt_video_from_images(
            slides_dir=args.slides_dir,
            output_dir=args.output_dir,
            video_mode=args.video_mode,
            video_duration=args.video_duration,
            slide_duration=args.slide_duration,
            video_quality=args.video_quality,
            max_concurrent=args.max_concurrent,
            skip_preview=args.skip_preview,
            prompts_file=args.prompts_file,
        )

        sys.exit(0 if result else 1)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Video Materials Generator Module.

Responsible for generating preview videos and transition videos for PPT slides.
Supports concurrent generation with configurable limits.
"""

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

from kling_api import KlingVideoGenerator
from prompt_file_reader import PromptFileReader


# =============================================================================
# Constants
# =============================================================================

DEFAULT_MAX_CONCURRENT = 3
DEFAULT_DURATION = "5"
DEFAULT_MODE = "pro"


# =============================================================================
# Video Materials Generator
# =============================================================================

class VideoMaterialsGenerator:
    """Generator for PPT video materials (preview and transition videos)."""

    def __init__(
        self,
        kling_client: Optional[KlingVideoGenerator] = None,
        prompt_generator: Optional[Any] = None,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT,
        prompts_file: Optional[str] = None,
    ) -> None:
        """
        Initialize video materials generator.

        Args:
            kling_client: Kling API client instance (created if not provided).
            prompt_generator: Custom prompt generator (prompts_file takes priority).
            max_concurrent: Maximum concurrent video generation tasks.
            prompts_file: Path to prompts JSON file (required if no prompt_generator).

        Raises:
            ValueError: If neither prompts_file nor prompt_generator is provided.
        """
        self.kling_client = kling_client or KlingVideoGenerator()
        self.max_concurrent = max_concurrent

        # Initialize prompt generator
        if prompts_file:
            self.prompt_generator = PromptFileReader(prompts_file)
            print(f"Using prompts file: {prompts_file}")
        elif prompt_generator:
            self.prompt_generator = prompt_generator
            print("Using custom prompt generator")
        else:
            raise ValueError(
                "Missing transition prompts.\n\n"
                "To generate video transitions, you need a prompts file.\n"
                "Follow these steps:\n"
                "1. In Claude Code, run:\n"
                "   'Analyze images in outputs/xxx/images, generate transition prompts,\n"
                "    save to outputs/xxx/transition_prompts.json'\n"
                "2. Use --prompts-file to specify the generated file path\n\n"
                "Example:\n"
                "  python generate_ppt_video.py \\\n"
                "    --slides-dir outputs/xxx/images \\\n"
                "    --output-dir outputs/xxx_video \\\n"
                "    --prompts-file outputs/xxx/transition_prompts.json"
            )

        print(f"Video materials generator initialized")
        print(f"  Max concurrent: {max_concurrent}")

    # -------------------------------------------------------------------------
    # Preview Video Generation
    # -------------------------------------------------------------------------

    def generate_preview_video(
        self,
        first_slide_path: str,
        output_dir: str,
        duration: str = DEFAULT_DURATION,
        mode: str = DEFAULT_MODE,
    ) -> Dict[str, Any]:
        """
        Generate preview video for the first slide (same first and last frame).

        Args:
            first_slide_path: Path to first slide image.
            output_dir: Output directory.
            duration: Video duration (5 or 10 seconds).
            mode: Generation mode (std/pro).

        Returns:
            Result dict with video_path, prompt, and duration.

        Raises:
            Exception: If video generation fails.
        """
        print("\n" + "=" * 80)
        print("Generating Preview Video")
        print("=" * 80)

        preview_prompt = self.prompt_generator.generate_preview_prompt(first_slide_path)

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "preview.mp4")

        print(f"\nGenerating preview video...")
        start_time = time.time()

        try:
            self.kling_client.generate_and_download(
                image_start=first_slide_path,
                image_end=first_slide_path,  # Same as start for looping
                prompt=preview_prompt,
                output_path=output_path,
                model_name="kling-v2-6",
                duration=duration,
                mode=mode,
            )

            elapsed = int(time.time() - start_time)

            print(f"\nPreview video generated!")
            print(f"  Duration: {elapsed}s")
            print(f"  Path: {output_path}\n")

            return {
                "video_path": output_path,
                "prompt": preview_prompt,
                "duration": elapsed,
            }

        except Exception as e:
            print(f"\nPreview video generation failed: {e}\n")
            raise

    # -------------------------------------------------------------------------
    # Transition Video Generation
    # -------------------------------------------------------------------------

    def _generate_single_transition(
        self,
        slide_from: str,
        slide_to: str,
        output_path: str,
        content_context: Optional[str] = None,
        duration: str = DEFAULT_DURATION,
        mode: str = DEFAULT_MODE,
    ) -> Dict[str, Any]:
        """
        Generate a single transition video.

        Args:
            slide_from: Source slide path.
            slide_to: Target slide path.
            output_path: Output video path.
            content_context: Content context for prompt generation.
            duration: Video duration.
            mode: Generation mode.

        Returns:
            Result dict with success status and details.
        """
        from_num = Path(slide_from).stem.split("-")[-1]
        to_num = Path(slide_to).stem.split("-")[-1]
        transition_key = f"{from_num}-{to_num}"

        print(f"\nGenerating transition [{transition_key}]")
        print(f"  {Path(slide_from).name} -> {Path(slide_to).name}")

        try:
            transition_prompt = self.prompt_generator.generate_prompt(
                frame_start_path=slide_from,
                frame_end_path=slide_to,
                content_context=content_context,
            )

            start_time = time.time()

            self.kling_client.generate_and_download(
                image_start=slide_from,
                image_end=slide_to,
                prompt=transition_prompt,
                output_path=output_path,
                model_name="kling-v2-6",
                duration=duration,
                mode=mode,
            )

            elapsed = int(time.time() - start_time)

            return {
                "from_to": transition_key,
                "video_path": output_path,
                "prompt": transition_prompt,
                "duration": elapsed,
                "success": True,
            }

        except Exception as e:
            return {
                "from_to": transition_key,
                "video_path": output_path,
                "prompt": "",
                "duration": 0,
                "success": False,
                "error": str(e),
            }

    def generate_transition_videos(
        self,
        slides_paths: List[str],
        output_dir: str,
        content_contexts: Optional[List[str]] = None,
        duration: str = DEFAULT_DURATION,
        mode: str = DEFAULT_MODE,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate all transition videos with concurrent execution.

        Args:
            slides_paths: List of slide image paths in order.
            output_dir: Output directory.
            content_contexts: Optional list of content contexts for each transition.
            duration: Video duration.
            mode: Generation mode.

        Returns:
            Dict mapping transition keys to result dicts.
        """
        print("\n" + "=" * 80)
        print("Generating Transition Videos")
        print("=" * 80)

        num_slides = len(slides_paths)
        num_transitions = num_slides - 1

        estimated_time_min = num_transitions * 100 / self.max_concurrent
        estimated_time_max = num_transitions * 120 / self.max_concurrent

        print(f"\nTask summary:")
        print(f"  Slides: {num_slides}")
        print(f"  Transitions: {num_transitions}")
        print(f"  Max concurrent: {self.max_concurrent}")
        print(f"  Estimated time: {estimated_time_min:.0f}-{estimated_time_max:.0f}s\n")

        os.makedirs(output_dir, exist_ok=True)

        # Prepare tasks
        tasks = []
        for i in range(num_transitions):
            from_num = Path(slides_paths[i]).stem.split("-")[-1]
            to_num = Path(slides_paths[i + 1]).stem.split("-")[-1]

            tasks.append({
                "slide_from": slides_paths[i],
                "slide_to": slides_paths[i + 1],
                "output_path": os.path.join(output_dir, f"transition_{from_num}_to_{to_num}.mp4"),
                "content_context": content_contexts[i] if content_contexts and i < len(content_contexts) else None,
            })

        # Execute with thread pool
        results: Dict[str, Dict[str, Any]] = {}
        completed_count = 0
        failed_count = 0

        print(f"Starting generation (concurrent: {self.max_concurrent})...\n")
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            future_to_task = {
                executor.submit(
                    self._generate_single_transition,
                    task["slide_from"],
                    task["slide_to"],
                    task["output_path"],
                    task["content_context"],
                    duration,
                    mode,
                ): task
                for task in tasks
            }

            for future in as_completed(future_to_task):
                result = future.result()
                transition_key = result["from_to"]
                results[transition_key] = result

                completed_count += 1

                if result["success"]:
                    print(f"  [{completed_count}/{num_transitions}] "
                          f"Transition {transition_key} complete ({result['duration']}s)")
                else:
                    failed_count += 1
                    print(f"  [{completed_count}/{num_transitions}] "
                          f"Transition {transition_key} failed: {result['error']}")

        total_elapsed = int(time.time() - start_time)

        # Summary
        print("\n" + "=" * 80)
        print("Transition Generation Complete")
        print("=" * 80)
        print(f"  Total time: {total_elapsed}s ({total_elapsed/60:.1f}m)")
        print(f"  Success: {num_transitions - failed_count}/{num_transitions}")
        print(f"  Failed: {failed_count}/{num_transitions}")

        if failed_count > 0:
            print(f"\n  Failed transitions:")
            for key, result in results.items():
                if not result["success"]:
                    print(f"    - {key}: {result['error']}")

        print("=" * 80 + "\n")

        return results

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    def save_metadata(self, output_dir: str, metadata: Dict[str, Any]) -> str:
        """
        Save generation metadata to JSON file.

        Args:
            output_dir: Output directory.
            metadata: Metadata dictionary.

        Returns:
            Path to saved metadata file.
        """
        metadata_path = os.path.join(output_dir, "video_metadata.json")

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"Metadata saved: {metadata_path}")
        return metadata_path

    # -------------------------------------------------------------------------
    # High-Level API
    # -------------------------------------------------------------------------

    def generate_all_materials(
        self,
        slides_paths: List[str],
        output_dir: str,
        content_contexts: Optional[List[str]] = None,
        duration: str = DEFAULT_DURATION,
        mode: str = DEFAULT_MODE,
        skip_preview: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate all video materials (preview + transitions) in one call.

        Args:
            slides_paths: List of slide image paths.
            output_dir: Output directory.
            content_contexts: Optional content contexts for transitions.
            duration: Video duration.
            mode: Generation mode.
            skip_preview: Whether to skip preview video generation.

        Returns:
            Complete results dict with preview, transitions, and statistics.
        """
        print("\n" + "=" * 80)
        print("Generating All Video Materials")
        print("=" * 80)

        total_start = time.time()

        all_results: Dict[str, Any] = {
            "preview": None,
            "transitions": {},
            "total_duration": 0,
            "success_count": 0,
            "failed_count": 0,
        }

        # Generate preview video
        if not skip_preview:
            try:
                preview_result = self.generate_preview_video(
                    first_slide_path=slides_paths[0],
                    output_dir=output_dir,
                    duration=duration,
                    mode=mode,
                )
                all_results["preview"] = preview_result
                all_results["success_count"] += 1
            except Exception as e:
                print(f"Warning: Preview generation failed, continuing: {e}")
                all_results["failed_count"] += 1
        else:
            print("Skipping preview video generation")

        # Generate transition videos
        transition_results = self.generate_transition_videos(
            slides_paths=slides_paths,
            output_dir=output_dir,
            content_contexts=content_contexts,
            duration=duration,
            mode=mode,
        )

        all_results["transitions"] = transition_results

        # Count successes/failures
        for result in transition_results.values():
            if result["success"]:
                all_results["success_count"] += 1
            else:
                all_results["failed_count"] += 1

        all_results["total_duration"] = int(time.time() - total_start)

        # Save metadata
        self.save_metadata(output_dir, all_results)

        # Final summary
        total_minutes = all_results["total_duration"] / 60
        print("\n" + "=" * 80)
        print("All Video Materials Generated!")
        print("=" * 80)
        print(f"  Total time: {all_results['total_duration']}s ({total_minutes:.1f}m)")
        print(f"  Success: {all_results['success_count']}")
        print(f"  Failed: {all_results['failed_count']}")
        print(f"  Output: {output_dir}")
        print("=" * 80 + "\n")

        return all_results


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("VideoMaterialsGenerator requires a prompts file to run.")
    print("Use generate_ppt_video.py for complete workflow.")

#!/usr/bin/env python3
"""
Simple Transition Prompt Generator.

Provides generic transition prompts without requiring Claude API.
Useful for testing or when Claude API is not available.
"""

from pathlib import Path
from typing import Optional


# =============================================================================
# Default Prompts
# =============================================================================

DEFAULT_TRANSITION_PROMPT = """The camera starts from the initial page, with background aurora waves flowing slowly from left to right. Neon purple, electric blue, and coral orange gradients shift gently against the dark background. The 3D glass object in the center begins to deconstruct, splitting into multiple transparent glass fragments that elegantly rotate and float in the air, reflecting the surrounding neon lights.

During deconstruction, the main elements of the starting page gradually disappear through fade-out, while new elements of the target page slowly emerge from transparency. If there are frosted glass rounded rectangle cards, they slide in from the edge or expand from the center, with subtle blur effects and reflections on their surfaces.

On the right side or other areas, glass fragments reassemble and weave into new 3D glass structures or data visualization graphics. These new elements are progressively assembled, each part maintaining the glass-morphic texture. If there are data labels or text information, they appear through simple fade-in, with text content remaining absolutely clear and stable throughout, without any distortion, blur, or shaking.

The aurora waves continue flowing throughout the transition, colors smoothly transitioning from the starting page's main tones to the target page's color scheme. Deep blue, purple, and coral gradients remain soft and coherent, creating a smooth, premium, tech-forward visual atmosphere. At the end, all elements stabilize in their final state, text is clear and readable, and glass objects are fully rendered."""

DEFAULT_PREVIEW_PROMPT = """The PPT cover composition remains static, with background aurora waves flowing extremely slowly from left to right. Neon purple, electric blue, and coral orange gradients breathe with subtle changes, completing a gentle brightness cycle over 5 seconds.

The central 3D glass object maintains its main form, but its surface reflections flow slowly, with glass material highlights shimmering like water waves, creating a subtle breathing sensation. If there are frosted glass cards, their edge glow intensity fluctuates subtly between 0.8 and 1.0.

Deep in the background, a few small light points may slowly drift in the darkness, like cosmic stardust. The overall brightness varies extremely subtly between 95% and 105% of normal value. All text content remains absolutely clear and stable, without any movement, distortion, or blur, always clearly readable.

This is a seamlessly looping subtle animation, where the last frame and first frame connect perfectly. The flow of light effects and color changes form a natural loop, giving a sense of serenity, premium quality, and waiting for interaction."""


# =============================================================================
# Simple Transition Prompt Generator
# =============================================================================

class SimpleTransitionPromptGenerator:
    """Simple prompt generator using generic templates."""

    def __init__(self) -> None:
        """Initialize simple prompt generator."""
        print("Simple prompt generator initialized")

    def generate_prompt(
        self,
        frame_start_path: str,
        frame_end_path: str,
        content_context: Optional[str] = None,
    ) -> str:
        """
        Generate generic transition prompt.

        Args:
            frame_start_path: Path to start frame image.
            frame_end_path: Path to end frame image.
            content_context: Ignored (for interface compatibility).

        Returns:
            Generic transition prompt text.
        """
        print(f"\nGenerating transition prompt...")
        print(f"  Start: {Path(frame_start_path).name}")
        print(f"  End: {Path(frame_end_path).name}")

        print("  Using generic transition template")
        print(f"\n{'=' * 60}")
        print(DEFAULT_TRANSITION_PROMPT)
        print(f"{'=' * 60}\n")

        return DEFAULT_TRANSITION_PROMPT

    def generate_preview_prompt(self, first_slide_path: str) -> str:
        """
        Generate generic preview prompt.

        Args:
            first_slide_path: Path to first slide image.

        Returns:
            Generic preview prompt text.
        """
        print(f"\nGenerating preview prompt...")
        print(f"  Slide: {Path(first_slide_path).name}")

        print("  Using generic preview template")

        return DEFAULT_PREVIEW_PROMPT


if __name__ == "__main__":
    import os

    generator = SimpleTransitionPromptGenerator()

    test_start = "outputs/20260112_012753/images/slide-01.png"
    test_end = "outputs/20260112_012753/images/slide-02.png"

    if os.path.exists(test_start) and os.path.exists(test_end):
        prompt = generator.generate_prompt(test_start, test_end)
        print(f"\nGenerated prompt length: {len(prompt)} characters")

    if os.path.exists(test_start):
        preview_prompt = generator.generate_preview_prompt(test_start)
        print(f"\nGenerated preview prompt length: {len(preview_prompt)} characters")

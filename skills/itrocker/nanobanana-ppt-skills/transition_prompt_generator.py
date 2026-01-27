#!/usr/bin/env python3
"""
Transition Prompt Generator Module.

Uses Claude AI to analyze slide images and generate transition descriptions
for video generation.
"""

import base64
import os
from pathlib import Path
from typing import Optional, Tuple

from anthropic import Anthropic


# =============================================================================
# Constants
# =============================================================================

DEFAULT_TEMPLATE_PATH = "prompts/transition_template.md"
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_MAX_TOKENS = 2000
DEFAULT_TEMPERATURE = 0.7

# Media type mapping
MEDIA_TYPE_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


# =============================================================================
# Exceptions
# =============================================================================

class PromptGeneratorError(Exception):
    """Exception for prompt generation errors."""
    pass


# =============================================================================
# Transition Prompt Generator
# =============================================================================

class TransitionPromptGenerator:
    """Generator for transition prompts using Claude AI."""

    def __init__(self, template_path: str = DEFAULT_TEMPLATE_PATH) -> None:
        """
        Initialize transition prompt generator.

        Args:
            template_path: Path to transition template markdown file.

        Raises:
            FileNotFoundError: If template file not found.
            PromptGeneratorError: If Claude API initialization fails.
        """
        self.template_path = template_path

        # Load template
        if not os.path.exists(template_path):
            raise FileNotFoundError(
                f"Transition template not found: {template_path}\n"
                "Please ensure the file exists."
            )

        with open(template_path, "r", encoding="utf-8") as f:
            self.template = f.read()

        print(f"Transition template loaded: {template_path}")

        # Initialize Claude client
        self.client = self._init_claude_client()
        print("Claude API client initialized")

    def _init_claude_client(self) -> Anthropic:
        """
        Initialize Claude API client.

        Returns:
            Configured Anthropic client.

        Raises:
            PromptGeneratorError: If initialization fails.
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")

        if api_key:
            return Anthropic(api_key=api_key)

        # Try default config (Claude Code environment)
        try:
            return Anthropic()
        except Exception as e:
            raise PromptGeneratorError(
                f"Claude API initialization failed.\n"
                f"Please set ANTHROPIC_API_KEY in .env file,\n"
                f"or run in Claude Code environment.\n"
                f"Error: {e}"
            )

    # -------------------------------------------------------------------------
    # Image Processing
    # -------------------------------------------------------------------------

    @staticmethod
    def _encode_image(image_path: str) -> Tuple[str, str]:
        """
        Encode image to base64 with media type.

        Args:
            image_path: Path to image file.

        Returns:
            Tuple of (base64_string, media_type).
        """
        with open(image_path, "rb") as f:
            image_data = f.read()

        base64_str = base64.standard_b64encode(image_data).decode("utf-8")

        ext = Path(image_path).suffix.lower()
        media_type = MEDIA_TYPE_MAP.get(ext, "image/jpeg")

        return base64_str, media_type

    # -------------------------------------------------------------------------
    # Prompt Generation
    # -------------------------------------------------------------------------

    def generate_prompt(
        self,
        frame_start_path: str,
        frame_end_path: str,
        content_context: Optional[str] = None,
    ) -> str:
        """
        Generate transition prompt by analyzing two frames.

        Args:
            frame_start_path: Path to start frame image.
            frame_end_path: Path to end frame image.
            content_context: Optional context about the content transition.

        Returns:
            Generated transition description.

        Raises:
            PromptGeneratorError: If API call fails.
        """
        print(f"\nAnalyzing transition scene...")
        print(f"  Start: {Path(frame_start_path).name}")
        print(f"  End: {Path(frame_end_path).name}")

        # Encode images
        start_b64, start_media = self._encode_image(frame_start_path)
        end_b64, end_media = self._encode_image(frame_end_path)

        # Build system message with text handling rules
        system_message = self.template + """

**Important - Text Handling Rules**:
1. Video models have issues with text (blur, distortion, garbled). Avoid text changes.
2. If there is text in the frame, explicitly state "text content remains clear and stable"
3. Prioritize transitions through background, decorations, lighting, and color changes
4. If text areas are involved, use fade in/out instead of transformation or movement
5. Avoid descriptions like "text gradually changes", "text moves", "text rotates"
6. Recommended: "text transitions via fade in/out", "text remains clear and stable"

Now, based on the provided [Start Frame] (Image A) and [End Frame] (Image B), generate your transition description.
"""

        if content_context:
            system_message += f"\n**Content Context**: {content_context}\n"

        system_message += "\nPlease generate the transition description."

        # Build multimodal message
        message_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": start_media,
                    "data": start_b64,
                },
            },
            {"type": "text", "text": "This is the [Start Frame] (Image A)"},
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": end_media,
                    "data": end_b64,
                },
            },
            {"type": "text", "text": "This is the [End Frame] (Image B)"},
            {"type": "text", "text": system_message},
        ]

        print("Calling Claude API for transition analysis...")

        try:
            response = self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=DEFAULT_MAX_TOKENS,
                temperature=DEFAULT_TEMPERATURE,
                messages=[{"role": "user", "content": message_content}],
            )

            transition_prompt = response.content[0].text.strip()

            print("Transition prompt generated!")
            print(f"\n{'=' * 60}")
            print(transition_prompt)
            print(f"{'=' * 60}\n")

            return transition_prompt

        except Exception as e:
            raise PromptGeneratorError(f"Claude API call failed: {e}")

    def generate_preview_prompt(self, first_slide_path: str) -> str:
        """
        Generate preview video prompt for first slide (looping animation).

        Args:
            first_slide_path: Path to first slide image.

        Returns:
            Generated preview animation description.

        Raises:
            PromptGeneratorError: If API call fails.
        """
        print(f"\nGenerating preview prompt...")
        print(f"  Slide: {Path(first_slide_path).name}")

        # Encode image
        image_b64, media_type = self._encode_image(first_slide_path)

        # Build message
        message_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_b64,
                },
            },
            {
                "type": "text",
                "text": """Please generate a subtle animation prompt for this PPT cover image, for a looping preview video.

Requirements:
1. First and last frames are the same image, video should loop seamlessly
2. Animation should be subtle and elegant, not exaggerated
3. Suggested animation types:
   - Light flow (aurora-like light slowly moving)
   - Glass surface breathing effect (subtle reflection changes)
   - Subtle background gradient color changes
   - Slow rotation of 3D objects (if present)
   - Particle effects (floating light dots)
4. **Important**: Text content must remain clear and stable, no changes, distortion or blur
5. Overall atmosphere should be serene, breathing, waiting to be clicked

Please describe this subtle animation in one paragraph (150-250 words).""",
            },
        ]

        print("Calling Claude API for preview prompt...")

        try:
            response = self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=1000,
                temperature=DEFAULT_TEMPERATURE,
                messages=[{"role": "user", "content": message_content}],
            )

            preview_prompt = response.content[0].text.strip()

            print("Preview prompt generated!")
            print(f"\n{'=' * 60}")
            print(preview_prompt)
            print(f"{'=' * 60}\n")

            return preview_prompt

        except Exception as e:
            raise PromptGeneratorError(f"Claude API call failed: {e}")


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == "__main__":
    print("TransitionPromptGenerator Test")
    print("=" * 60)

    try:
        generator = TransitionPromptGenerator()
        print("\nGenerator initialized successfully.")
        print("To test, provide slide image paths.")
    except Exception as e:
        print(f"Initialization failed: {e}")

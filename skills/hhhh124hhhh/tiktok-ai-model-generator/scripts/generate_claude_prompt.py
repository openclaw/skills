#!/usr/bin/env python3
"""
Generate detailed JSON prompt for TikTok AI model video workflow.

This script creates structured prompts for Nano Banana Pro based on
Pinterest references and product descriptions.

Usage:
    python generate_claude_prompt.py --product "gold necklace" --pinterest "model looking down" --lighting "studio"
"""

import argparse
import json
import sys


def create_json_prompt(product, pose, angle, lighting, model_appearance, outfit, expression, background, location, atmosphere, style):
    """
    Create structured JSON prompt for Nano Banana Pro.

    Args:
        product (str): Product description to be included
        pose (str): Pose description from Pinterest reference
        angle (str): Camera angle
        lighting (str): Lighting style
        model_appearance (str): Model physical appearance
        outfit (str): Clothing/style details
        expression (str): Facial expression
        background (str): Background description
        location (str): Setting/context
        atmosphere (str): Mood/vibe
        style (str): Photography style

    Returns:
        str: JSON formatted prompt
    """

    prompt = {
        "subject": {
            "description": product,
            "pose": pose,
            "angle": angle,
            "lighting": lighting
        },
        "model": {
            "appearance": model_appearance,
            "outfit": outfit,
            "expression": expression
        },
        "environment": {
            "background": background,
            "location": location,
            "atmosphere": atmosphere
        },
        "technical": {
            "style": style,
            "camera": "Professional DSLR, 85mm lens",
            "resolution": "1024x1024"
        }
    }

    return json.dumps(prompt, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Generate JSON prompt for Nano Banana Pro"
    )
    parser.add_argument(
        "--product",
        required=True,
        help="Product description (e.g., 'gold necklace', 'white t-shirt')"
    )
    parser.add_argument(
        "--pose",
        required=True,
        help="Pose from Pinterest (e.g., 'standing upright', 'looking down')"
    )
    parser.add_argument(
        "--angle",
        default="full body",
        choices=["full body", "upper body", "close-up", "profile", "three-quarter"],
        help="Camera angle (default: full body)"
    )
    parser.add_argument(
        "--lighting",
        default="studio lighting",
        help="Lighting style (default: studio lighting)"
    )
    parser.add_argument(
        "--model-appearance",
        default="young adult, natural look",
        help="Model physical appearance (default: young adult, natural look)"
    )
    parser.add_argument(
        "--outfit",
        default="casual minimalist",
        help="Clothing style (default: casual minimalist)"
    )
    parser.add_argument(
        "--expression",
        default="relaxed and confident",
        help="Facial expression (default: relaxed and confident)"
    )
    parser.add_argument(
        "--background",
        default="pure white seamless",
        help="Background description (default: pure white seamless)"
    )
    parser.add_argument(
        "--location",
        default="studio environment",
        help="Setting/context (default: studio environment)"
    )
    parser.add_argument(
        "--atmosphere",
        default="professional and clean",
        help="Mood/vibe (default: professional and clean)"
    )
    parser.add_argument(
        "--style",
        default="photorealistic, commercial photography",
        help="Photography style (default: photorealistic, commercial photography)"
    )

    args = parser.parse_args()

    # Generate JSON prompt
    prompt_json = create_json_prompt(
        product=args.product,
        pose=args.pose,
        angle=args.angle,
        lighting=args.lighting,
        model_appearance=args.model_appearance,
        outfit=args.outfit,
        expression=args.expression,
        background=args.background,
        location=args.location,
        atmosphere=args.atmosphere,
        style=args.style
    )

    # Output
    print("=" * 80)
    print("NANO BANANA PRO JSON PROMPT")
    print("=" * 80)
    print()
    print(prompt_json)
    print()
    print("=" * 80)
    print("PROMPT FOR CLAUDE:")
    print("=" * 80)
    print()
    print(f"Give me detailed JSON prompt for this Pinterest image holding {args.product}:")
    print(prompt_json)
    print()
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Copy the JSON prompt above")
    print("2. Open Nano Banana Pro (https://higgsfield.ai)")
    print("3. Upload your product image (white background)")
    print("4. Paste the JSON prompt")
    print("5. Click Generate")
    print("6. Animate with Veo/Kling")


if __name__ == "__main__":
    main()

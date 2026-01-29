#!/usr/bin/env python3
"""
AI Video Generator - End-to-end video creation from text prompts
Supports: OpenAI DALL-E, Replicate, LumaAI, Runway, FFmpeg
"""

import os
import sys
import argparse
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API clients
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
LUMAAI_API_KEY = os.getenv('LUMAAI_API_KEY')
RUNWAY_API_KEY = os.getenv('RUNWAY_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')


class VideoGenerator:
    def __init__(self, output_dir='output'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_image_openai(self, prompt, size="1024x1024"):
        """Generate image using DALL-E 3"""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
            
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        print(f"🎨 Generating image with DALL-E 3: {prompt[:50]}...")
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        
        # Download image
        img_path = self.output_dir / f"image_{int(time.time())}.png"
        img_data = requests.get(image_url).content
        with open(img_path, 'wb') as f:
            f.write(img_data)
            
        print(f"✓ Image saved: {img_path}")
        return str(img_path)
    
    def generate_image_replicate(self, prompt, model="stability-ai/sdxl"):
        """Generate image using Replicate (Stable Diffusion, Flux, etc.)"""
        if not REPLICATE_API_TOKEN:
            raise ValueError("REPLICATE_API_TOKEN not set")
            
        import replicate
        
        print(f"🎨 Generating image with {model}: {prompt[:50]}...")
        
        output = replicate.run(
            model,
            input={"prompt": prompt}
        )
        
        # Download image
        img_path = self.output_dir / f"image_{int(time.time())}.png"
        if isinstance(output, list):
            img_data = requests.get(output[0]).content
        else:
            img_data = requests.get(output).content
            
        with open(img_path, 'wb') as f:
            f.write(img_data)
            
        print(f"✓ Image saved: {img_path}")
        return str(img_path)
    
    def image_to_video_luma(self, image_path, prompt=None):
        """Convert image to video using LumaAI"""
        if not LUMAAI_API_KEY:
            raise ValueError("LUMAAI_API_KEY not set")
            
        print(f"🎬 Creating video from image with LumaAI...")
        
        headers = {
            "Authorization": f"Bearer {LUMAAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Upload image and create video
        # This is a placeholder - actual LumaAI API structure may vary
        data = {
            "image": image_path,
            "prompt": prompt or "animate this image"
        }
        
        response = requests.post(
            "https://api.lumalabs.ai/dream-machine/v1/generations",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"LumaAI API error: {response.text}")
            
        generation_id = response.json()['id']
        
        # Poll for completion
        while True:
            status = requests.get(
                f"https://api.lumalabs.ai/dream-machine/v1/generations/{generation_id}",
                headers=headers
            ).json()
            
            if status['state'] == 'completed':
                video_url = status['video']['url']
                break
            elif status['state'] == 'failed':
                raise Exception(f"Video generation failed: {status}")
            
            print("⏳ Waiting for video generation...")
            time.sleep(5)
        
        # Download video
        video_path = self.output_dir / f"video_{int(time.time())}.mp4"
        video_data = requests.get(video_url).content
        with open(video_path, 'wb') as f:
            f.write(video_data)
            
        print(f"✓ Video saved: {video_path}")
        return str(video_path)
    
    def add_audio_openai(self, text, voice="alloy"):
        """Generate audio using OpenAI TTS"""
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
            
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        print(f"🎤 Generating voiceover: {text[:50]}...")
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        audio_path = self.output_dir / f"audio_{int(time.time())}.mp3"
        response.stream_to_file(str(audio_path))
        
        print(f"✓ Audio saved: {audio_path}")
        return str(audio_path)
    
    def combine_video_audio(self, video_path, audio_path, output_path):
        """Combine video and audio using FFmpeg"""
        import subprocess
        
        print(f"🎞️ Combining video and audio...")
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
            
        print(f"✓ Final video saved: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description='Generate AI videos from text prompts')
    parser.add_argument('--prompt', required=True, help='Text prompt for video generation')
    parser.add_argument('--voiceover', help='Text for voiceover narration')
    parser.add_argument('--output', default='output.mp4', help='Output video file')
    parser.add_argument('--image-model', choices=['dalle', 'replicate'], default='dalle', help='Image generation model')
    parser.add_argument('--video-model', choices=['luma', 'runway'], default='luma', help='Video generation model')
    parser.add_argument('--voice', default='alloy', help='Voice for TTS (alloy, echo, fable, onyx, nova, shimmer)')
    
    args = parser.parse_args()
    
    try:
        generator = VideoGenerator()
        
        # Step 1: Generate image
        if args.image_model == 'dalle':
            image_path = generator.generate_image_openai(args.prompt)
        else:
            image_path = generator.generate_image_replicate(args.prompt)
        
        # Step 2: Convert to video
        if args.video_model == 'luma':
            video_path = generator.image_to_video_luma(image_path, args.prompt)
        else:
            print("⚠️ Runway support coming soon. Using Luma for now.")
            video_path = generator.image_to_video_luma(image_path, args.prompt)
        
        # Step 3: Add voiceover if requested
        if args.voiceover:
            audio_path = generator.add_audio_openai(args.voiceover, args.voice)
            final_path = generator.combine_video_audio(video_path, audio_path, args.output)
        else:
            # Just rename/move the video
            os.rename(video_path, args.output)
            final_path = args.output
        
        print(f"\n✅ SUCCESS! Video created: {final_path}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

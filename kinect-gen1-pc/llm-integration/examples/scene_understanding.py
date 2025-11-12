#!/usr/bin/env python3
"""
Scene Understanding with Kinect + LLM Vision
Describes what the Kinect sees using Claude or GPT-4 Vision
"""

import freenect
import cv2
import numpy as np
import base64
import json
import os
from io import BytesIO
from PIL import Image
import sys

try:
    from anthropic import Anthropic
except ImportError:
    print("anthropic not installed. Install with: pip install anthropic")
    Anthropic = None

try:
    import openai
except ImportError:
    print("openai not installed. Install with: pip install openai")
    openai = None

class KinectSceneAnalyzer:
    """Analyze Kinect scenes using LLM vision models"""

    def __init__(self, model="claude", api_key=None):
        """
        Initialize analyzer

        Args:
            model: "claude" or "gpt4"
            api_key: API key (or set in environment)
        """
        self.model_type = model

        if model == "claude":
            if not Anthropic:
                raise ImportError("Install: pip install anthropic")

            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Set ANTHROPIC_API_KEY environment variable")

            self.client = Anthropic(api_key=api_key)
            self.model = "claude-3-5-sonnet-20241022"

        elif model == "gpt4":
            if not openai:
                raise ImportError("Install: pip install openai")

            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Set OPENAI_API_KEY environment variable")

            openai.api_key = api_key
            self.client = openai.OpenAI(api_key=api_key)
            self.model = "gpt-4o"

    def rgb_to_base64(self, rgb_array):
        """Convert numpy RGB array to base64 JPEG"""
        # Convert to PIL Image
        image = Image.fromarray(rgb_array)

        # Convert to JPEG in memory
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)

        # Encode to base64
        return base64.b64encode(buffer.read()).decode()

    def analyze_with_claude(self, rgb, prompt):
        """Analyze image with Claude"""
        image_data = self.rgb_to_base64(rgb)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }]
        )

        return response.content[0].text

    def analyze_with_gpt4(self, rgb, prompt):
        """Analyze image with GPT-4 Vision"""
        image_data = self.rgb_to_base64(rgb)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1024
        )

        return response.choices[0].message.content

    def describe_scene(self, rgb):
        """Get general scene description"""
        prompt = "Please describe what you see in this image. Include: people, objects, activities, and the overall setting."

        if self.model_type == "claude":
            return self.analyze_with_claude(rgb, prompt)
        else:
            return self.analyze_with_gpt4(rgb, prompt)

    def ask(self, question, rgb):
        """Ask specific question about the scene"""
        if self.model_type == "claude":
            return self.analyze_with_claude(rgb, question)
        else:
            return self.analyze_with_gpt4(rgb, question)

    def find_objects(self, rgb):
        """List all visible objects"""
        prompt = "List all objects visible in this image. Return as a JSON array of object names."

        result = self.ask(prompt, rgb)

        # Try to parse JSON
        try:
            # Extract JSON from response
            start = result.find('[')
            end = result.rfind(']') + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
        except:
            pass

        # Fallback: return as text
        return result

    def analyze_with_depth(self, rgb, depth, query):
        """
        Analyze scene with depth information
        Adds depth context to the query
        """
        # Calculate some depth statistics
        valid_depth = depth[depth > 0]
        if len(valid_depth) > 0:
            min_dist = valid_depth.min() / 1000.0  # Convert to meters
            max_dist = valid_depth.max() / 1000.0
            avg_dist = valid_depth.mean() / 1000.0

            depth_context = f"\n\nDepth information: Objects in this scene range from {min_dist:.2f}m to {max_dist:.2f}m from the camera. Average depth is {avg_dist:.2f}m."
        else:
            depth_context = ""

        full_query = query + depth_context

        return self.ask(full_query, rgb)

def main():
    print("Kinect Scene Understanding with LLM")
    print("=" * 50)

    # Choose model
    model = os.getenv("VISION_MODEL", "claude")  # or "gpt4"
    print(f"Using model: {model}")
    print()

    # Check Kinect
    try:
        ctx = freenect.init()
        if freenect.num_devices(ctx) < 1:
            print("ERROR: No Kinect found!")
            return 1
        print("✓ Kinect detected")
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

    # Initialize analyzer
    try:
        analyzer = KinectSceneAnalyzer(model=model)
        print("✓ LLM vision model initialized")
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nMake sure to set your API key:")
        print("  export ANTHROPIC_API_KEY=your-key  # for Claude")
        print("  export OPENAI_API_KEY=your-key     # for GPT-4")
        return 1

    print()
    print("Controls:")
    print("  SPACE - Analyze current scene")
    print("  d - Describe scene in detail")
    print("  o - Find objects")
    print("  q - Ask custom question")
    print("  s - Save image")
    print("  ESC - Quit")
    print("=" * 50)
    print()

    analyzing = False
    analysis_text = ""

    try:
        while True:
            # Capture frame
            rgb, _ = freenect.sync_get_video()
            depth, _ = freenect.sync_get_depth()

            # Convert to BGR for display
            display = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

            # Show analysis result
            if analysis_text:
                # Word wrap the text
                words = analysis_text.split()
                lines = []
                current_line = []
                for word in words:
                    current_line.append(word)
                    test_line = ' '.join(current_line)
                    if len(test_line) > 60:
                        lines.append(' '.join(current_line[:-1]))
                        current_line = [word]
                if current_line:
                    lines.append(' '.join(current_line))

                # Display lines
                y = 30
                for line in lines[:10]:  # Max 10 lines
                    cv2.putText(display, line, (10, y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    y += 20

            if analyzing:
                cv2.putText(display, "Analyzing...", (10, display.shape[0] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow('Kinect Scene Understanding', display)

            # Handle keyboard
            key = cv2.waitKey(10) & 0xFF

            if key == 27:  # ESC
                break

            elif key == ord(' ') and not analyzing:
                # Quick analysis
                analyzing = True
                analysis_text = "Analyzing..."
                cv2.imshow('Kinect Scene Understanding', display)
                cv2.waitKey(1)

                try:
                    analysis_text = analyzer.describe_scene(rgb)
                    print("\n" + "=" * 50)
                    print("SCENE ANALYSIS:")
                    print(analysis_text)
                    print("=" * 50)
                except Exception as e:
                    analysis_text = f"Error: {e}"
                    print(f"Error: {e}")

                analyzing = False

            elif key == ord('d') and not analyzing:
                # Detailed description
                analyzing = True
                analysis_text = "Analyzing in detail..."
                cv2.imshow('Kinect Scene Understanding', display)
                cv2.waitKey(1)

                try:
                    analysis_text = analyzer.analyze_with_depth(
                        rgb, depth,
                        "Provide a detailed description of this scene, including spatial layout and distances where relevant."
                    )
                    print("\n" + "=" * 50)
                    print("DETAILED ANALYSIS:")
                    print(analysis_text)
                    print("=" * 50)
                except Exception as e:
                    analysis_text = f"Error: {e}"
                    print(f"Error: {e}")

                analyzing = False

            elif key == ord('o') and not analyzing:
                # Find objects
                analyzing = True
                analysis_text = "Finding objects..."
                cv2.imshow('Kinect Scene Understanding', display)
                cv2.waitKey(1)

                try:
                    objects = analyzer.find_objects(rgb)
                    analysis_text = f"Objects: {', '.join(objects) if isinstance(objects, list) else objects}"
                    print("\n" + "=" * 50)
                    print("OBJECTS FOUND:")
                    print(objects)
                    print("=" * 50)
                except Exception as e:
                    analysis_text = f"Error: {e}"
                    print(f"Error: {e}")

                analyzing = False

            elif key == ord('q') and not analyzing:
                # Custom question
                print("\nEnter your question: ", end='', flush=True)

                # Pause display to get input
                cv2.waitKey(1)

                question = input()
                if question:
                    analyzing = True
                    analysis_text = "Processing question..."
                    cv2.imshow('Kinect Scene Understanding', display)
                    cv2.waitKey(1)

                    try:
                        answer = analyzer.ask(question, rgb)
                        analysis_text = f"Q: {question}\nA: {answer}"
                        print("\n" + "=" * 50)
                        print(f"Q: {question}")
                        print(f"A: {answer}")
                        print("=" * 50)
                    except Exception as e:
                        analysis_text = f"Error: {e}"
                        print(f"Error: {e}")

                    analyzing = False

            elif key == ord('s'):
                # Save image
                import time
                filename = f"kinect_scene_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, display)
                print(f"Saved: {filename}")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    finally:
        cv2.destroyAllWindows()
        freenect.sync_stop()

    return 0

if __name__ == "__main__":
    sys.exit(main())

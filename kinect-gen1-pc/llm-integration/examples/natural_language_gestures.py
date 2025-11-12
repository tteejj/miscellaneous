#!/usr/bin/env python3
"""
Natural Language Gesture Recognition with Kinect + LLM
Define gestures using plain English descriptions instead of code!

Example:
    "Person raising both hands above their head"
    "Person waving their right hand"
    "Person making a thumbs up gesture"
"""

import freenect
import cv2
import numpy as np
import base64
import json
import os
import time
from io import BytesIO
from PIL import Image
import sys

try:
    from anthropic import Anthropic
except ImportError:
    print("anthropic not installed. Install with: pip install anthropic")
    sys.exit(1)

class NaturalLanguageGesture:
    """Detect gestures defined in natural language"""

    def __init__(self, api_key=None):
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Set ANTHROPIC_API_KEY environment variable")

        self.client = Anthropic(api_key=api_key)
        self.gestures = {}
        self.last_detection = None
        self.cooldown = 2.0  # seconds between detections
        self.last_time = 0

    def rgb_to_base64(self, rgb_array):
        """Convert numpy RGB array to base64 JPEG"""
        image = Image.fromarray(rgb_array)
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=75)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode()

    def add_gesture(self, name, description, action=None):
        """
        Add a gesture to detect

        Args:
            name: Unique name for gesture
            description: Natural language description
            action: Function to call when detected (optional)
        """
        self.gestures[name] = {
            'description': description,
            'action': action
        }
        print(f"✓ Added gesture: {name}")
        print(f"  Description: {description}")

    def detect(self, rgb_frame, confidence_threshold=0.7):
        """
        Detect if any registered gesture is present

        Returns:
            gesture_name or None
        """
        # Cooldown check
        current_time = time.time()
        if current_time - self.last_time < self.cooldown:
            return None

        # Build prompt with all gesture descriptions
        gesture_list = "\n".join([
            f"{i+1}. {name}: {info['description']}"
            for i, (name, info) in enumerate(self.gestures.items())
        ])

        prompt = f"""Analyze this image and determine if the person is performing any of these gestures:

{gesture_list}

Respond with ONLY a JSON object in this exact format:
{{
    "detected": "gesture_name" or null,
    "confidence": 0.0 to 1.0,
    "explanation": "brief explanation"
}}

If no gesture matches, set "detected" to null.
Be strict - only return a gesture if you're confident it matches the description."""

        try:
            image_data = self.rgb_to_base64(rgb_frame)

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=256,
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

            result_text = response.content[0].text

            # Parse JSON response
            # Find JSON in response
            start = result_text.find('{')
            end = result_text.rfind('}') + 1

            if start >= 0 and end > start:
                result = json.loads(result_text[start:end])

                detected = result.get('detected')
                confidence = result.get('confidence', 0.0)
                explanation = result.get('explanation', '')

                if detected and confidence >= confidence_threshold:
                    self.last_detection = detected
                    self.last_time = current_time
                    print(f"\n🎯 Gesture detected: {detected}")
                    print(f"   Confidence: {confidence:.2f}")
                    print(f"   {explanation}")
                    return detected

        except Exception as e:
            print(f"Detection error: {e}")

        return None

    def execute(self, gesture_name):
        """Execute action for detected gesture"""
        if gesture_name in self.gestures:
            action = self.gestures[gesture_name]['action']
            if action:
                try:
                    action()
                except Exception as e:
                    print(f"Error executing action: {e}")

    def remove_gesture(self, name):
        """Remove a gesture"""
        if name in self.gestures:
            del self.gestures[name]
            print(f"✗ Removed gesture: {name}")

def main():
    print("Natural Language Gesture Recognition")
    print("=" * 50)

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

    # Initialize gesture system
    try:
        nlg = NaturalLanguageGesture()
        print("✓ Gesture system initialized")
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nSet your API key:")
        print("  export ANTHROPIC_API_KEY=your-key")
        return 1

    print()

    # Define some example gestures
    print("Defining example gestures...")
    print()

    nlg.add_gesture(
        "wave",
        "Person waving their hand (moving hand side to side in greeting)",
        action=lambda: print("👋 Action: Hello!")
    )

    nlg.add_gesture(
        "thumbs_up",
        "Person showing a thumbs up gesture (hand with thumb extended upward)",
        action=lambda: print("👍 Action: Approved!")
    )

    nlg.add_gesture(
        "peace_sign",
        "Person making a peace sign or victory sign (two fingers extended in V shape)",
        action=lambda: print("✌️ Action: Peace!")
    )

    nlg.add_gesture(
        "hands_up",
        "Person raising both hands above their head",
        action=lambda: print("🙌 Action: Celebration!")
    )

    nlg.add_gesture(
        "pointing",
        "Person pointing at something with their index finger extended",
        action=lambda: print("👉 Action: Look there!")
    )

    print()
    print("=" * 50)
    print("Ready! Perform gestures in front of the Kinect.")
    print()
    print("Controls:")
    print("  SPACE - Manually trigger detection")
    print("  a - Add custom gesture")
    print("  l - List gestures")
    print("  c - Clear cooldown")
    print("  ESC - Quit")
    print("=" * 50)
    print()

    auto_detect = True
    detecting = False
    frame_count = 0
    detect_interval = 45  # Check every ~1.5 seconds at 30fps

    try:
        while True:
            # Capture
            rgb, _ = freenect.sync_get_video()

            # Convert for display
            display = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

            # Show status
            if detecting:
                cv2.putText(display, "Analyzing gesture...", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Show last detection
            if nlg.last_detection:
                cv2.putText(display, f"Last: {nlg.last_detection}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Show cooldown
            time_since = time.time() - nlg.last_time
            if time_since < nlg.cooldown:
                remaining = nlg.cooldown - time_since
                cv2.putText(display, f"Cooldown: {remaining:.1f}s", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            cv2.imshow('Natural Language Gestures', display)

            # Auto-detect at intervals
            if auto_detect and not detecting:
                frame_count += 1
                if frame_count >= detect_interval:
                    frame_count = 0
                    detecting = True

                    # Update display
                    cv2.imshow('Natural Language Gestures', display)
                    cv2.waitKey(1)

                    # Detect
                    detected = nlg.detect(rgb)
                    if detected:
                        nlg.execute(detected)

                    detecting = False

            # Keyboard input
            key = cv2.waitKey(10) & 0xFF

            if key == 27:  # ESC
                break

            elif key == ord(' ') and not detecting:
                # Manual detection
                detecting = True
                print("\nManual detection triggered...")

                # Update display
                cv2.imshow('Natural Language Gestures', display)
                cv2.waitKey(1)

                detected = nlg.detect(rgb)
                if detected:
                    nlg.execute(detected)
                else:
                    print("No gesture detected")

                detecting = False

            elif key == ord('a'):
                # Add custom gesture
                print("\n" + "=" * 50)
                print("ADD CUSTOM GESTURE")
                print("=" * 50)

                name = input("Gesture name: ").strip()
                if name:
                    description = input("Describe the gesture: ").strip()
                    if description:
                        nlg.add_gesture(name, description,
                                       action=lambda n=name: print(f"✨ {n} detected!"))
                        print(f"\n✓ Gesture '{name}' added!")
                    else:
                        print("Cancelled - no description")
                else:
                    print("Cancelled - no name")

                print("=" * 50)

            elif key == ord('l'):
                # List gestures
                print("\n" + "=" * 50)
                print("REGISTERED GESTURES:")
                print("=" * 50)
                for i, (name, info) in enumerate(nlg.gestures.items(), 1):
                    print(f"{i}. {name}")
                    print(f"   Description: {info['description']}")
                    print()
                print("=" * 50)

            elif key == ord('c'):
                # Clear cooldown
                nlg.last_time = 0
                print("Cooldown cleared")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    finally:
        cv2.destroyAllWindows()
        freenect.sync_stop()

    print("\nGesture system stopped")
    return 0

if __name__ == "__main__":
    sys.exit(main())

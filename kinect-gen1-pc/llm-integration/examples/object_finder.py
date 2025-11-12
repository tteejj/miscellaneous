#!/usr/bin/env python3
"""
Object Finder with Kinect + LLM
Find objects by asking "Where are my keys?", "Find the coffee mug", etc.
Uses LLM vision to identify objects and depth to report distances
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
from datetime import datetime

try:
    from anthropic import Anthropic
except ImportError:
    print("anthropic not installed. Install with: pip install anthropic")
    sys.exit(1)

class ObjectFinder:
    """Find and locate objects using LLM vision + Kinect depth"""

    def __init__(self, api_key=None):
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Set ANTHROPIC_API_KEY environment variable")

        self.client = Anthropic(api_key=api_key)
        self.memory = {}  # Object memory

    def rgb_to_base64(self, rgb_array):
        """Convert numpy RGB array to base64 JPEG"""
        image = Image.fromarray(rgb_array)
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode()

    def find_object(self, rgb, depth, object_name):
        """
        Find specific object in scene

        Returns:
            dict with location info or None
        """
        image_data = self.rgb_to_base64(rgb)

        prompt = f"""Find the {object_name} in this image.

Respond with ONLY a JSON object in this exact format:
{{
    "found": true or false,
    "location": "description of where it is (e.g., 'on the desk', 'left side of frame')",
    "bbox": [x, y, width, height],
    "center": [x, y],
    "confidence": 0.0 to 1.0
}}

The bbox and center should be in pixel coordinates (image is 640x480).
If the object is not found, set "found" to false and other fields to null."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
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

            # Parse JSON
            start = result_text.find('{')
            end = result_text.rfind('}') + 1

            if start >= 0 and end > start:
                result = json.loads(result_text[start:end])

                if result.get('found'):
                    # Add depth information
                    center = result.get('center')
                    if center and depth is not None:
                        x, y = int(center[0]), int(center[1])
                        # Ensure coordinates are valid
                        x = max(0, min(x, depth.shape[1] - 1))
                        y = max(0, min(y, depth.shape[0] - 1))

                        # Get depth at object center (average small region)
                        region_size = 10
                        x1 = max(0, x - region_size)
                        x2 = min(depth.shape[1], x + region_size)
                        y1 = max(0, y - region_size)
                        y2 = min(depth.shape[0], y + region_size)

                        depth_region = depth[y1:y2, x1:x2]
                        valid_depths = depth_region[depth_region > 0]

                        if len(valid_depths) > 0:
                            distance_mm = np.median(valid_depths)
                            distance_m = distance_mm / 1000.0
                            result['distance_m'] = round(distance_m, 2)
                        else:
                            result['distance_m'] = None

                    return result

        except Exception as e:
            print(f"Error finding object: {e}")

        return None

    def remember_object(self, object_name, rgb, depth):
        """Remember where an object is"""
        result = self.find_object(rgb, depth, object_name)

        if result and result.get('found'):
            self.memory[object_name] = {
                'location': result.get('location'),
                'distance_m': result.get('distance_m'),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'confidence': result.get('confidence')
            }
            return True
        return False

    def recall_object(self, object_name):
        """Recall where an object was last seen"""
        return self.memory.get(object_name)

    def list_memory(self):
        """List all remembered objects"""
        return self.memory

    def scan_scene(self, rgb, depth):
        """Identify all objects in scene"""
        image_data = self.rgb_to_base64(rgb)

        prompt = """List all significant objects visible in this image.

Respond with ONLY a JSON array of objects in this format:
[
    {
        "name": "object name",
        "location": "where it is",
        "center": [x, y]
    },
    ...
]

Focus on identifying distinct, nameable objects."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
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

            result_text = response.content[0].text

            # Parse JSON array
            start = result_text.find('[')
            end = result_text.rfind(']') + 1

            if start >= 0 and end > start:
                objects = json.loads(result_text[start:end])

                # Add depth info for each object
                for obj in objects:
                    center = obj.get('center')
                    if center and depth is not None:
                        x, y = int(center[0]), int(center[1])
                        x = max(0, min(x, depth.shape[1] - 1))
                        y = max(0, min(y, depth.shape[0] - 1))

                        region_size = 10
                        x1 = max(0, x - region_size)
                        x2 = min(depth.shape[1], x + region_size)
                        y1 = max(0, y - region_size)
                        y2 = min(depth.shape[0], y + region_size)

                        depth_region = depth[y1:y2, x1:x2]
                        valid_depths = depth_region[depth_region > 0]

                        if len(valid_depths) > 0:
                            distance_m = np.median(valid_depths) / 1000.0
                            obj['distance_m'] = round(distance_m, 2)

                return objects

        except Exception as e:
            print(f"Error scanning scene: {e}")

        return []

def main():
    print("Kinect Object Finder with LLM")
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

    # Initialize finder
    try:
        finder = ObjectFinder()
        print("✓ Object finder initialized")
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nSet your API key:")
        print("  export ANTHROPIC_API_KEY=your-key")
        return 1

    print()
    print("Controls:")
    print("  f - Find specific object")
    print("  s - Scan scene for all objects")
    print("  r - Remember object location")
    print("  m - Show memory")
    print("  c - Clear memory")
    print("  i - Save image")
    print("  ESC - Quit")
    print("=" * 50)
    print()

    searching = False

    try:
        while True:
            # Capture
            rgb, _ = freenect.sync_get_video()
            depth, _ = freenect.sync_get_depth()

            # Display
            display = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

            if searching:
                cv2.putText(display, "Searching...", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow('Object Finder', display)

            # Keyboard
            key = cv2.waitKey(10) & 0xFF

            if key == 27:  # ESC
                break

            elif key == ord('f') and not searching:
                # Find object
                print("\nWhat object do you want to find?")
                print("Object name: ", end='', flush=True)

                cv2.waitKey(1)
                object_name = input().strip()

                if object_name:
                    searching = True
                    print(f"Searching for: {object_name}...")

                    cv2.imshow('Object Finder', display)
                    cv2.waitKey(1)

                    result = finder.find_object(rgb, depth, object_name)

                    if result and result.get('found'):
                        print(f"\n✓ Found {object_name}!")
                        print(f"  Location: {result.get('location')}")
                        if result.get('distance_m'):
                            print(f"  Distance: {result.get('distance_m')}m")
                        print(f"  Confidence: {result.get('confidence'):.2f}")

                        # Draw on image
                        bbox = result.get('bbox')
                        if bbox:
                            x, y, w, h = bbox
                            cv2.rectangle(display, (int(x), int(y)),
                                        (int(x+w), int(y+h)), (0, 255, 0), 2)
                            cv2.putText(display, object_name, (int(x), int(y-10)),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                        cv2.imshow('Object Finder', display)
                        cv2.waitKey(3000)  # Show for 3 seconds
                    else:
                        print(f"\n✗ Could not find {object_name}")

                    searching = False

            elif key == ord('s') and not searching:
                # Scan scene
                searching = True
                print("\nScanning scene...")

                cv2.imshow('Object Finder', display)
                cv2.waitKey(1)

                objects = finder.scan_scene(rgb, depth)

                print(f"\n✓ Found {len(objects)} objects:")
                print("=" * 50)
                for i, obj in enumerate(objects, 1):
                    print(f"{i}. {obj.get('name')}")
                    print(f"   Location: {obj.get('location')}")
                    if obj.get('distance_m'):
                        print(f"   Distance: {obj.get('distance_m')}m")
                print("=" * 50)

                searching = False

            elif key == ord('r') and not searching:
                # Remember object
                print("\nWhat object should I remember?")
                print("Object name: ", end='', flush=True)

                cv2.waitKey(1)
                object_name = input().strip()

                if object_name:
                    searching = True
                    print(f"Looking for {object_name}...")

                    cv2.imshow('Object Finder', display)
                    cv2.waitKey(1)

                    if finder.remember_object(object_name, rgb, depth):
                        print(f"✓ Remembered location of {object_name}")
                    else:
                        print(f"✗ Could not find {object_name}")

                    searching = False

            elif key == ord('m'):
                # Show memory
                memory = finder.list_memory()

                print("\n" + "=" * 50)
                print("OBJECT MEMORY:")
                print("=" * 50)

                if memory:
                    for obj_name, info in memory.items():
                        print(f"\n{obj_name}:")
                        print(f"  Location: {info.get('location')}")
                        if info.get('distance_m'):
                            print(f"  Distance: {info.get('distance_m')}m")
                        print(f"  Last seen: {info.get('timestamp')}")
                        print(f"  Confidence: {info.get('confidence'):.2f}")
                else:
                    print("(empty)")

                print("=" * 50)

            elif key == ord('c'):
                # Clear memory
                finder.memory.clear()
                print("Memory cleared")

            elif key == ord('i'):
                # Save image
                filename = f"kinect_objects_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, display)
                print(f"Saved: {filename}")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    finally:
        cv2.destroyAllWindows()
        freenect.sync_stop()

    print("\nObject finder stopped")
    return 0

if __name__ == "__main__":
    sys.exit(main())

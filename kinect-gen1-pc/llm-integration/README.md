# LLM Integration with Kinect Gen 1

Combine Large Language Models and computer vision for intelligent, context-aware Kinect applications.

## Table of Contents
1. [Overview](#overview)
2. [What LLMs Can Do](#what-llms-can-do)
3. [Setup](#setup)
4. [Scene Understanding](#scene-understanding)
5. [Natural Language Gestures](#natural-language-gestures)
6. [Interactive Applications](#interactive-applications)
7. [Local vs Cloud Models](#local-vs-cloud-models)

## Overview

Modern LLMs with vision capabilities can:
- **Understand scenes** from Kinect RGB camera
- **Interpret gestures** in natural language
- **Respond to visual queries** about what Kinect sees
- **Provide context** for depth data
- **Enable accessibility** through scene description
- **Smart object detection** beyond simple CV

**Advantages over traditional CV:**
- No training data needed for new objects
- Natural language interaction
- Context-aware responses
- Understands complex scenes
- Can explain what it sees

**Combining with depth:**
- 3D understanding (RGB + depth)
- Distance to identified objects
- Spatial relationships
- Better segmentation

## What LLMs Can Do

### 1. Scene Description
```python
# What does the Kinect see?
describe_scene(rgb_frame)
# → "A person sitting at a desk with a laptop and coffee mug.
#     There's a bookshelf in the background."
```

### 2. Object Identification
```python
# What objects are present?
identify_objects(rgb_frame)
# → ["laptop", "coffee mug", "book", "plant"]

# Where is the laptop?
find_object(rgb_frame, "laptop")
# → Returns bounding box + depth from Kinect
```

### 3. Gesture Interpretation
```python
# What gesture am I doing?
interpret_gesture(rgb_frame)
# → "You're waving your right hand"

# Am I pointing at something?
check_pointing(rgb_frame, depth_frame)
# → "Yes, pointing at the monitor, approximately 0.8m away"
```

### 4. Natural Language Commands
```python
# User: "Turn on the lights when I raise both hands"
# LLM: Creates gesture detector for that specific action
# Much more flexible than pre-programmed gestures!
```

### 5. Accessibility
```python
# Describe surroundings for visually impaired
describe_environment(rgb_frame, depth_frame)
# → "There's a table 1.2 meters ahead, chairs on both sides.
#     A doorway is 3 meters to your left."
```

### 6. Activity Recognition
```python
# What am I doing?
recognize_activity(video_frames)
# → "You appear to be exercising - doing jumping jacks"
```

## Setup

### Install Dependencies

```bash
# Base requirements (already installed)
pip install numpy opencv-python freenect

# For OpenAI GPT-4 Vision
pip install openai

# For Anthropic Claude (vision)
pip install anthropic

# For local models (LLaVA, etc.)
pip install torch torchvision
pip install transformers
pip install pillow

# For advanced features
pip install requests
pip install python-dotenv  # For API keys
```

### API Keys Setup

Create `.env` file in project root:

```bash
# OpenAI (GPT-4 Vision)
OPENAI_API_KEY=sk-your-key-here

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: Local models don't need keys
```

### Quick Test

```python
# Test vision model with static image
from anthropic import Anthropic
import base64

client = Anthropic()

with open("test_image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

response = client.messages.create(
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
                "text": "What do you see in this image?"
            }
        ]
    }]
)

print(response.content[0].text)
```

## Scene Understanding

### Basic Scene Analysis

```python
# See examples/scene_understanding.py for full code
from kinect_llm import KinectSceneAnalyzer

analyzer = KinectSceneAnalyzer(model="claude-3-5-sonnet-20241022")

# Capture from Kinect
rgb, _ = freenect.sync_get_video()
depth, _ = freenect.sync_get_depth()

# Get scene description
description = analyzer.describe_scene(rgb)
print(description)

# Ask specific questions
answer = analyzer.ask("Is anyone sitting at the desk?", rgb)
print(answer)

# Identify objects with positions
objects = analyzer.find_objects(rgb, depth)
# Returns: [{"name": "laptop", "bbox": (x,y,w,h), "distance": 1.2}]
```

### Depth-Enhanced Understanding

```python
# Combine RGB understanding with depth data
analyzer.analyze_with_depth(rgb, depth,
    query="How far away is the person?")
# → "The person is approximately 1.5 meters from the sensor"

analyzer.analyze_with_depth(rgb, depth,
    query="What objects are within arm's reach?")
# → Identifies objects < 1m away
```

### Continuous Monitoring

```python
# Monitor scene changes
monitor = SceneMonitor(model="gpt-4o")

while True:
    rgb, _ = freenect.sync_get_video()

    changes = monitor.detect_changes(rgb)
    if changes:
        print(f"Scene changed: {changes}")
        # → "New person entered the room"
        # → "Object moved on desk"
```

See `examples/scene_understanding.py`

## Natural Language Gestures

### Define Gestures in Natural Language

Instead of programming gesture detectors, describe them:

```python
from kinect_llm import NaturalLanguageGesture

nlg = NaturalLanguageGesture()

# Define gestures with plain English
nlg.add_gesture(
    name="victory",
    description="Person making a peace sign with their hand",
    action=lambda: print("Victory!")
)

nlg.add_gesture(
    name="thumbs_up",
    description="Person showing thumbs up gesture",
    action=toggle_lights
)

nlg.add_gesture(
    name="pointing_left",
    description="Person pointing to their left",
    action=previous_slide
)

# Run detection
while True:
    rgb, _ = freenect.sync_get_video()
    detected = nlg.detect(rgb)
    if detected:
        nlg.execute(detected)
```

### Context-Aware Gestures

```python
# Gestures that depend on context
nlg.add_contextual_gesture(
    name="pick_up_object",
    description="Person reaching toward an object and grasping it",
    context_check=lambda scene: "object" in scene.lower(),
    action=handle_pickup
)
```

### User-Trainable Gestures

```python
# Let users create their own gestures!
nlg.train_gesture(
    name="my_custom_gesture",
    description=input("Describe your gesture: "),
    action=lambda: print("Custom gesture triggered!")
)

# User: "Raising both hands above my head"
# System learns and can detect this gesture
```

See `examples/natural_language_gestures.py`

## Interactive Applications

### 1. Visual Question Answering

Ask questions about what Kinect sees:

```bash
python examples/visual_qa.py
```

```
You: What color is my shirt?
AI: Your shirt appears to be blue.

You: How many people are in the room?
AI: I can see one person in the frame.

You: What's on the desk behind me?
AI: On the desk I can see a laptop, a coffee mug, and some papers.

You: How far am I from the camera?
AI: Based on the depth data, you're approximately 1.8 meters away.
```

### 2. Smart Home Control

Natural language + vision:

```python
# "Turn on lights when someone enters the room"
controller = SmartHomeVisionController()

controller.add_rule(
    trigger="person enters frame",
    action="turn_on_lights"
)

controller.add_rule(
    trigger="room is empty for 5 minutes",
    action="turn_off_lights"
)

controller.add_rule(
    trigger="person waves at camera",
    action="toggle_music"
)
```

See `examples/smart_home_vision.py`

### 3. Accessibility Assistant

Help visually impaired navigate:

```python
assistant = AccessibilityAssistant()

while True:
    rgb, depth = capture_kinect()

    # Describe environment
    if button_pressed():
        description = assistant.describe_surroundings(rgb, depth)
        text_to_speech(description)
        # → "Table 1.2m ahead, chair on left at 2m, doorway at 3m"

    # Obstacle warning
    obstacles = assistant.detect_obstacles(depth)
    if obstacles:
        warn_user(obstacles)
```

See `examples/accessibility_assistant.py`

### 4. Fitness Form Checker

Check exercise form with AI:

```python
coach = AIFitnessCoach()

exercise = "squat"
frames = capture_video_sequence(5)  # 5 seconds

analysis = coach.check_form(frames, exercise)
print(analysis)
# → "Good depth! But keep your knees aligned with your toes.
#     Your back is straight - excellent form overall."

# Get depth-enhanced feedback
with_depth = coach.check_form_3d(frames, depth_frames, exercise)
# → "Your squat depth is approximately 40cm - try to go deeper"
```

See `examples/fitness_coach.py`

### 5. Interactive Storytelling

Scene-aware story generation:

```python
storyteller = InteractiveStoryteller()

while True:
    rgb, _ = freenect.sync_get_video()

    # Generate story based on what it sees
    story_segment = storyteller.continue_story(rgb)
    print(story_segment)

    # User can influence with gestures
    # Wave = plot twist, point = focus on object, etc.
```

See `examples/interactive_story.py`

### 6. Object Memory

Remember where you put things:

```python
memory = ObjectMemory()

# AI watches and remembers
while running:
    rgb, depth = capture_kinect()

    # User: "Remember where my keys are"
    if voice_command == "remember keys":
        memory.remember_object("keys", rgb, depth)

    # Later: "Where are my keys?"
    if voice_command == "find keys":
        location = memory.recall_object("keys")
        print(location)
        # → "Your keys are on the desk, approximately 1.5m away"
```

See `examples/object_memory.py`

## Local vs Cloud Models

### Cloud-Based (API)

**Pros:**
- Best accuracy
- Latest models
- No hardware requirements
- Fast updates

**Cons:**
- Requires internet
- API costs
- Privacy concerns (data sent to cloud)
- Latency

**Best for:**
- High-quality scene understanding
- Complex reasoning
- Non-real-time applications
- When accuracy matters most

**Models:**
- Claude 3.5 Sonnet (excellent vision, fast)
- GPT-4o (great all-around)
- Gemini Pro Vision (good, cost-effective)

### Local Models

**Pros:**
- Complete privacy
- No internet needed
- No API costs
- Real-time possible

**Cons:**
- Requires powerful hardware (GPU)
- Lower accuracy than cloud
- More complex setup

**Best for:**
- Privacy-sensitive applications
- Offline use
- Real-time requirements
- Cost-conscious projects

**Models:**
- LLaVA (7B, 13B variants)
- MiniGPT-4
- Qwen-VL
- CogVLM

### Hybrid Approach

Best of both worlds:

```python
class HybridVisionModel:
    def __init__(self):
        self.local = LocalVisionModel()  # Fast, always available
        self.cloud = ClaudeVision()      # Accurate, for complex tasks

    def analyze(self, image, complexity="auto"):
        # Simple queries → local
        if complexity == "simple":
            return self.local.analyze(image)

        # Complex queries → cloud
        elif complexity == "complex":
            return self.cloud.analyze(image)

        # Auto-detect
        else:
            # Try local first
            result, confidence = self.local.analyze_with_confidence(image)

            # Fall back to cloud if uncertain
            if confidence < 0.8:
                return self.cloud.analyze(image)

            return result
```

### Setup Local Models

```bash
# Install Ollama (easiest for local models)
curl -fsSL https://ollama.com/install.sh | sh

# Download vision model
ollama pull llava

# Test
ollama run llava "Describe this image" < image.jpg
```

Python integration:

```python
import requests
import json
import base64

def analyze_with_llava(image_path, prompt):
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    response = requests.post("http://localhost:11434/api/generate",
        json={
            "model": "llava",
            "prompt": prompt,
            "images": [image_data]
        },
        stream=True
    )

    result = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            result += data.get("response", "")

    return result
```

## Performance Optimization

### 1. Frame Sampling

Don't send every frame:

```python
# Send every Nth frame
frame_skip = 10
frame_count = 0

while True:
    rgb, depth = capture_kinect()

    frame_count += 1
    if frame_count % frame_skip == 0:
        analysis = llm.analyze(rgb)
```

### 2. Region of Interest

Only analyze relevant parts:

```python
# Focus on center where person typically is
h, w = rgb.shape[:2]
roi = rgb[h//4:3*h//4, w//4:3*w//4]

analysis = llm.analyze(roi)
```

### 3. Caching

Cache similar scenes:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def analyze_scene_cached(image_hash, prompt):
    return llm.analyze(image_from_hash(image_hash), prompt)

# Use hash to detect duplicate/similar scenes
image_hash = hashlib.md5(rgb.tobytes()).hexdigest()
result = analyze_scene_cached(image_hash, "What do you see?")
```

### 4. Async Processing

Don't block main thread:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

async def process_frame_async(rgb):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        llm.analyze,
        rgb
    )
    return result

# Main loop stays responsive
while True:
    rgb, depth = capture_kinect()

    # Non-blocking analysis
    asyncio.create_task(process_frame_async(rgb))

    # Continue with other tasks
```

## Example Scripts

All in `examples/llm-integration/` directory:

**Basic:**
- `scene_understanding.py` - Describe what Kinect sees
- `visual_qa.py` - Ask questions about the scene
- `object_finder.py` - Find objects by name

**Gestures:**
- `natural_language_gestures.py` - Define gestures with words
- `gesture_trainer.py` - Let users create custom gestures

**Applications:**
- `smart_home_vision.py` - Vision-based home automation
- `accessibility_assistant.py` - Navigation help
- `fitness_coach.py` - Exercise form checker
- `object_memory.py` - Remember where things are
- `interactive_story.py` - Scene-aware storytelling

**Setup:**
- `setup_ollama.sh` - Install local models
- `test_vision_models.py` - Compare different models

## Cost Considerations

**API Costs (approximate):**

**GPT-4 Vision:**
- ~$0.01 per image (depending on detail level)
- 30 fps → $18/minute (impractical)
- 1 frame/5 sec → $0.12/minute (reasonable)

**Claude 3.5 Sonnet:**
- ~$0.003 per image
- More cost-effective for frequent analysis

**Gemini Pro Vision:**
- Free tier: 60 queries/minute
- Cost-effective for experimentation

**Local models:**
- Zero cost after setup
- Hardware investment: GPU recommended

**Recommendations:**
- Use local for real-time, cloud for quality
- Sample frames (not every frame)
- Batch process when possible
- Cache common scenes

## Privacy & Security

**Cloud models:**
- Images sent to provider's servers
- Check terms of service
- Consider data sensitivity
- May be stored/used for training

**Local models:**
- All processing on your machine
- No data leaves your system
- Full privacy control

**Best practices:**
- Use local models for sensitive applications
- Implement opt-in for cloud features
- Clear user notification
- Allow offline mode

## Next Steps

1. **Try basic scene understanding:**
   ```bash
   python examples/llm-integration/scene_understanding.py
   ```

2. **Experiment with visual QA:**
   ```bash
   python examples/llm-integration/visual_qa.py
   ```

3. **Create custom natural language gestures**

4. **Build your own LLM-powered Kinect app!**

---

**The combination of Kinect's depth sensing and LLM vision creates powerful new possibilities!**

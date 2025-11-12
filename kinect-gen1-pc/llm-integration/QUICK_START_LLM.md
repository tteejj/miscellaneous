# Quick Start: LLM + Kinect Integration

Get AI-powered vision running with your Kinect in 10 minutes!

## What You Get

With LLM integration, your Kinect can:
- **Understand scenes** ("What do you see?" → "A person at a desk with a laptop")
- **Find objects** ("Where are my keys?" → "On the desk, 1.2m away")
- **Recognize gestures naturally** ("Wave", "Thumbs up" - just describe them!)
- **Answer questions** about what it sees
- **Remember locations** of objects

## Choose Your Model

### Option 1: Cloud API (Easiest, Best Quality)

**Claude 3.5 Sonnet (Recommended)**
- Excellent vision understanding
- Fast responses
- Cost: ~$0.003 per image
- Sign up: https://console.anthropic.com/

**GPT-4o (Alternative)**
- Great all-around
- Cost: ~$0.01 per image
- Sign up: https://platform.openai.com/

### Option 2: Local Models (Privacy, No Cost)

**LLaVA via Ollama**
- Run entirely on your machine
- No API costs
- Requires: GPU recommended (8GB+ VRAM)
- See setup below

## Quick Setup (Claude - Recommended)

### 1. Install Dependencies

```bash
cd kinect-gen1-pc/llm-integration
pip install -r requirements.txt
```

This installs:
- `anthropic` - Claude API client
- `openai` - GPT-4 client (optional)
- `python-dotenv` - Environment variables

### 2. Get API Key

**For Claude:**
1. Go to https://console.anthropic.com/
2. Sign up / Log in
3. Go to "API Keys"
4. Create new key
5. Copy the key (starts with `sk-ant-...`)

**For OpenAI:**
1. Go to https://platform.openai.com/
2. Sign up / Log in
3. Go to API Keys
4. Create new key
5. Copy the key (starts with `sk-...`)

### 3. Set API Key

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Make it permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.bashrc
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Make it permanent
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-your-key-here', 'User')
```

**Or use .env file:**
```bash
# Create .env in project root
cd kinect-gen1-pc
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
```

### 4. Test It!

```bash
cd llm-integration/examples

# Scene understanding
python scene_understanding.py

# Press SPACE to analyze what Kinect sees
# Press 'q' to ask questions
```

**That's it!** The Kinect can now understand what it sees.

## Try the Examples

### 1. Scene Understanding

Describe what the Kinect sees:

```bash
python scene_understanding.py
```

**Controls:**
- `SPACE` - Describe scene
- `d` - Detailed analysis (with depth)
- `o` - Find all objects
- `q` - Ask custom question

**Example:**
```
You: [Press q] "What color is my shirt?"
AI: "Your shirt appears to be blue."

You: "How far am I from the camera?"
AI: "Based on the depth data, approximately 1.5 meters."
```

### 2. Object Finder

Find specific objects and remember where they are:

```bash
python object_finder.py
```

**Controls:**
- `f` - Find object ("Where are my keys?")
- `s` - Scan scene for all objects
- `r` - Remember object location
- `m` - Show memory

**Example:**
```
[Press f]
Object name: coffee mug

✓ Found coffee mug!
  Location: On the desk, center-left
  Distance: 1.3m
  Confidence: 0.92
```

Later:
```
[Press m] - Shows all remembered objects
```

### 3. Natural Language Gestures

Define gestures in plain English:

```bash
python natural_language_gestures.py
```

**Pre-defined gestures:**
- Wave → "Hello!"
- Thumbs up → "Approved!"
- Peace sign → "Peace!"
- Both hands up → "Celebration!"

**Add your own:**
```
[Press a]
Gesture name: my_gesture
Describe the gesture: Person touching their nose with their finger
✓ Gesture 'my_gesture' added!
```

Now just perform the gesture - AI will detect it!

## Local Models Setup (Optional)

Want to run everything on your machine with no API costs?

### Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Mac:**
```bash
brew install ollama
```

**Windows:**
Download from https://ollama.com/download

### Download LLaVA Model

```bash
ollama pull llava
```

This downloads a vision-capable model (~4GB).

### Use Local Model

Modify the example scripts to use Ollama:

```python
# Instead of Claude/GPT-4, use local model
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

## Cost & Usage Tips

### API Costs

**Claude 3.5 Sonnet:**
- $3 per 1,000 images
- $0.003 per image
- Example: 100 images/day = $9/month

**GPT-4o:**
- $10 per 1,000 images
- $0.01 per image
- Example: 100 images/day = $30/month

### Reduce Costs

1. **Don't analyze every frame!**
   ```python
   # Sample every 30 frames (~1 per second at 30fps)
   if frame_count % 30 == 0:
       analyze(frame)
   ```

2. **Lower image quality**
   ```python
   # Reduce resolution
   small_img = cv2.resize(rgb, (320, 240))
   analyze(small_img)
   ```

3. **Use local models** for real-time, cloud for quality
   ```python
   # Quick check with local
   result_local = local_model.analyze(frame)

   # If unsure, use cloud
   if result_local.confidence < 0.8:
       result = cloud_model.analyze(frame)
   ```

## What to Build

### Ideas for LLM + Kinect Projects

1. **Smart Security Camera**
   - "Alert me if someone is at the door"
   - "Notify when a package is delivered"
   - Natural language event detection

2. **Personal Assistant**
   - "What's on my desk?"
   - "Did I leave my keys here?"
   - "How many people in the room?"

3. **Accessibility Tool**
   - Describe surroundings for visually impaired
   - "What's in front of me?"
   - "Is the path clear?"

4. **Fitness Coach**
   - "Check my squat form"
   - "Count my push-ups"
   - Natural language feedback

5. **Interactive Art**
   - React to what people are doing
   - Generate stories based on scenes
   - Creative installations

6. **Teaching Aid**
   - "What shape is this?"
   - "Identify the colors present"
   - Educational interactions

## Troubleshooting

### "API key not found"

Make sure environment variable is set:
```bash
echo $ANTHROPIC_API_KEY  # Linux/Mac
echo $env:ANTHROPIC_API_KEY  # Windows

# Should print your key (sk-ant-...)
```

### "Rate limit exceeded"

API has usage limits:
- Slow down requests
- Increase time between analyses
- Check your API usage dashboard

### "Model not responding"

Check internet connection (for cloud models) or Ollama status (local):
```bash
ollama list  # Should show llava
curl http://localhost:11434/  # Should respond
```

### High latency

- Use local models for real-time
- Reduce image resolution
- Cache similar scenes
- Async processing

### Poor accuracy

- Use better lighting
- Increase image quality
- Try different prompt wording
- Use Claude/GPT-4 for better results
- Provide more context in prompts

## Privacy Considerations

**Cloud APIs:**
- Images sent to provider servers
- Check provider's privacy policy
- May be used for model training (opt-out available)
- Internet required

**Local models:**
- Everything stays on your machine
- No data sent anywhere
- Works offline
- Full privacy control

**Recommendation:**
- Use local for privacy-sensitive applications
- Use cloud for best quality when privacy isn't critical

## Next Steps

1. **Try all three examples** to understand capabilities
2. **Read the full README** for advanced features
3. **Combine with other Kinect features:**
   - LLM + gesture control = Smart gestures
   - LLM + 3D scanning = Automatic object labeling
   - LLM + depth = Spatial understanding
4. **Build your own application!**

## More Examples Coming

Check `examples/` directory for additional scripts:
- `accessibility_assistant.py` - Vision-based navigation
- `fitness_coach.py` - Form checking
- `smart_home_vision.py` - Home automation
- `interactive_story.py` - Creative applications

---

**Questions?** Check the main LLM integration README for detailed documentation.

**Ready to make your Kinect truly intelligent!** 🧠🎥

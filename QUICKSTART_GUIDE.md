# 🚀 Quick Start Guide: Clone, Test & Run Voice Cloning API

Complete step-by-step instructions to get your Voice Cloning API running in VS Code.

---

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] **Git** installed ([Download](https://git-scm.com/downloads))
- [ ] **Python 3.9-3.12** installed ([Download](https://www.python.org/downloads/))
- [ ] **VS Code** installed ([Download](https://code.visualstudio.com/))
- [ ] **FFmpeg** installed (required for audio processing)

### Install FFmpeg:

**Windows:**
```powershell
# Using Chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Verify FFmpeg:**
```bash
ffmpeg -version
```

---

## 🔽 STEP 1: Clone Repository to VS Code

### Method A: Using VS Code Interface (Easiest)

1. **Open VS Code**

2. **Press** `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)

3. **Type:** `Git: Clone`

4. **Paste Repository URL:**
   ```
   https://github.com/GodsonicCodes/Real-Time-Voice-Cloning.git
   ```

5. **Select Folder** where you want to save the project

6. **Click "Open"** when VS Code asks to open the cloned repository

### Method B: Using Terminal in VS Code

1. **Open VS Code**

2. **Open Terminal:** View → Terminal (or `` Ctrl+` ``)

3. **Navigate to your projects folder:**
   ```bash
   cd ~/Documents/Projects  # Change to your preferred location
   ```

4. **Clone the repository:**
   ```bash
   git clone https://github.com/GodsonicCodes/Real-Time-Voice-Cloning.git
   cd Real-Time-Voice-Cloning
   ```

5. **Open in VS Code:**
   ```bash
   code .
   ```

### Method C: Using Git Bash/Command Line

```bash
# Navigate to your projects folder
cd ~/Documents/Projects

# Clone repository
git clone https://github.com/GodsonicCodes/Real-Time-Voice-Cloning.git

# Open in VS Code
cd Real-Time-Voice-Cloning
code .
```

---

## ⚙️ STEP 2: Set Up Python Environment

### 2.1 Install VS Code Python Extension

1. **Click Extensions** icon in left sidebar (or `Ctrl+Shift+X`)
2. **Search for:** "Python"
3. **Install** the official Python extension by Microsoft

### 2.2 Create Virtual Environment

**In VS Code Terminal:**

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### 2.3 Install API Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install API requirements
pip install -r api/requirements.txt
```

**⏰ This will take 3-5 minutes** (downloads ~2GB of packages including PyTorch, TTS models, etc.)

**Expected output:**
```
Successfully installed TTS-0.21.0 fastapi-0.109.0 ...
```

---

## 🧪 STEP 3: Test the Installation

### 3.1 Quick Test Script

Create a test file to verify everything works:

```bash
# Create test script
cat > test_installation.py << 'EOF'
#!/usr/bin/env python3
"""Quick installation test"""

print("🔍 Testing Voice Cloning API Installation\n")
print("=" * 50)

# Test 1: Python packages
print("\n1. Testing Python packages...")
try:
    import fastapi
    import TTS
    import torch
    import librosa
    print("   ✅ All required packages installed")
except ImportError as e:
    print(f"   ❌ Missing package: {e}")
    exit(1)

# Test 2: PyTorch device
print("\n2. Checking PyTorch device...")
if torch.cuda.is_available():
    print(f"   ✅ GPU available: {torch.cuda.get_device_name(0)}")
    print(f"   ✅ CUDA version: {torch.version.cuda}")
else:
    print("   ℹ️  GPU not available, will use CPU")
    print("   (This is fine, just slower)")

# Test 3: TTS Model
print("\n3. Testing TTS model access...")
try:
    from TTS.api import TTS
    # Don't actually load model (takes time), just check import
    print("   ✅ TTS module accessible")
except Exception as e:
    print(f"   ❌ TTS error: {e}")
    exit(1)

# Test 4: API modules
print("\n4. Testing API modules...")
try:
    from api import config, models, tts_service, voice_manager
    print("   ✅ All API modules importable")
except ImportError as e:
    print(f"   ❌ API import error: {e}")
    exit(1)

# Test 5: FFmpeg
print("\n5. Checking FFmpeg...")
import subprocess
try:
    result = subprocess.run(['ffmpeg', '-version'],
                          capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        version = result.stdout.split('\n')[0]
        print(f"   ✅ {version}")
    else:
        print("   ❌ FFmpeg not working properly")
except FileNotFoundError:
    print("   ❌ FFmpeg not found in PATH")
    print("   Please install: https://ffmpeg.org/download.html")
except subprocess.TimeoutExpired:
    print("   ❌ FFmpeg timeout")

print("\n" + "=" * 50)
print("🎉 Installation test complete!\n")
EOF

# Run the test
python test_installation.py
```

**Expected Output:**
```
🔍 Testing Voice Cloning API Installation

==================================================

1. Testing Python packages...
   ✅ All required packages installed

2. Checking PyTorch device...
   ℹ️  GPU not available, will use CPU

3. Testing TTS model access...
   ✅ TTS module accessible

4. Testing API modules...
   ✅ All API modules importable

5. Checking FFmpeg...
   ✅ ffmpeg version 6.0

==================================================
🎉 Installation test complete!
```

### 3.2 Test Voice Cloning (Optional)

If you want to test actual voice cloning:

```bash
# This will take ~2 minutes on first run (downloads models)
python test_voice_clone.py
```

---

## 🚀 STEP 4: Run the API

### Method 1: Using Uvicorn (Recommended)

```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Run the API
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
============================================================
Starting Voice Cloning API for AI Phone Agents v1.0.0
============================================================
INFO:     Loading XTTS v2 model on device: cpu
INFO:     ✓ TTS service initialized on cpu
INFO:     ✓ Voice library initialized with 6 voices
============================================================
🚀 API ready at http://0.0.0.0:8000
📚 Docs at http://0.0.0.0:8000/api/v1/docs
============================================================
INFO:     Application startup complete.
```

### Method 2: Using Quick Start Script

```bash
chmod +x start_api.sh
./start_api.sh
```

### Method 3: Using VS Code Debugger

1. **Create** `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Voice API",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "api.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ],
            "jinja": true,
            "justMyCode": false
        }
    ]
}
```

2. **Press** `F5` to start debugging

---

## 🧪 STEP 5: Test the API

### 5.1 Open Interactive Documentation

**In your browser, open:**
```
http://localhost:8000/api/v1/docs
```

You should see the **Swagger UI** with all API endpoints!

### 5.2 Test Health Endpoint

**Method A: Using Browser**

Open: `http://localhost:8000/api/v1/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "device": "cpu",
  "uptime_seconds": 45.2
}
```

**Method B: Using curl (Terminal)**

```bash
curl http://localhost:8000/api/v1/health
```

**Method C: Using VS Code REST Client**

1. Install "REST Client" extension
2. Create `test_api.http`:

```http
### Health Check
GET http://localhost:8000/api/v1/health

### List Voices
GET http://localhost:8000/api/v1/voices

### Synthesize Speech
POST http://localhost:8000/api/v1/speak
Content-Type: application/json

{
  "text": "Hello! This is a test of the voice cloning system.",
  "voice_id": "sample_1320_00000",
  "emotion": "friendly",
  "telephony_format": false
}
```

3. Click "Send Request" above each section

### 5.3 Test Voice Synthesis (Full Test)

**Using the Swagger UI:**

1. Go to `http://localhost:8000/api/v1/docs`

2. Find **POST `/api/v1/speak`**

3. Click **"Try it out"**

4. Enter test data:
   ```json
   {
     "text": "Hello Sarah, I'm calling about your appointment tomorrow.",
     "voice_id": "sample_1320_00000",
     "context": "greeting",
     "emotion": "friendly",
     "speed": 1.0,
     "add_naturals": true,
     "streaming": false,
     "telephony_format": false,
     "language": "en"
   }
   ```

5. Click **"Execute"**

6. **Download the audio** from the response `audio_url`

**Using curl:**

```bash
# Generate speech
curl -X POST "http://localhost:8000/api/v1/speak" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello! Testing voice cloning API.",
    "voice_id": "sample_1320_00000",
    "emotion": "friendly"
  }' | python -m json.tool

# Expected response:
# {
#   "audio_url": "/api/v1/audio/abc12345.wav",
#   "duration": 2.5,
#   "processing_time": 1.2,
#   "real_time_factor": 0.48
# }

# Download the generated audio
curl http://localhost:8000/api/v1/audio/abc12345.wav -o test_output.wav

# Play the audio (macOS)
afplay test_output.wav

# Play the audio (Linux)
aplay test_output.wav

# Play the audio (Windows)
start test_output.wav
```

---

## 📊 STEP 6: Verify Performance

### 6.1 Check Metrics

```bash
curl http://localhost:8000/api/v1/metrics | python -m json.tool
```

**Expected Output:**
```json
{
  "total_requests": 5,
  "total_audio_generated_seconds": 12.5,
  "average_latency_ms": 850.5,
  "average_rtf": 0.42,
  "cache_hit_rate": 0.0,
  "active_voices": 6
}
```

### 6.2 Check Available Voices

```bash
curl http://localhost:8000/api/v1/voices | python -m json.tool
```

**Expected Output:**
```json
{
  "voices": [
    {
      "voice_id": "sample_1320_00000",
      "name": "Sample Voice 1320_00000",
      "description": "Default sample voice",
      "tags": ["sample", "default"],
      "sample_count": 1,
      "total_duration": 8.5,
      "quality_score": 0.87
    }
  ],
  "total": 6
}
```

---

## 🎤 STEP 7: Add Your Own Voice

### 7.1 Prepare Voice Sample

Requirements:
- **Duration:** 5-30 seconds
- **Format:** WAV, MP3, FLAC, or M4A
- **Quality:** Clear speech, minimal background noise
- **Content:** Natural speech (not robotic)
- **Speaker:** Single speaker only

### 7.2 Upload Voice via API

**Method A: Using Swagger UI**

1. Go to `http://localhost:8000/api/v1/docs`
2. Find **POST `/api/v1/voices`**
3. Click "Try it out"
4. Fill in:
   - `voice_data`:
     ```json
     {
       "voice_id": "my_custom_voice",
       "name": "My Custom Voice",
       "description": "My personal voice for testing",
       "tags": ["custom", "test"]
     }
     ```
   - `audio_file`: Click "Choose File" and select your audio
5. Click "Execute"

**Method B: Using curl**

```bash
curl -X POST "http://localhost:8000/api/v1/voices" \
  -F "audio_file=@/path/to/your/voice_sample.wav" \
  -F 'voice_data={
    "voice_id": "my_custom_voice",
    "name": "My Custom Voice",
    "description": "My personal voice",
    "tags": ["custom"]
  }'
```

### 7.3 Test Your Voice

```bash
# Preview your voice
curl "http://localhost:8000/api/v1/voices/my_custom_voice/preview?text=Hello%20world" \
  -o my_voice_test.wav

# Or synthesize with your voice
curl -X POST "http://localhost:8000/api/v1/speak" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is my cloned voice speaking!",
    "voice_id": "my_custom_voice",
    "emotion": "friendly"
  }'
```

---

## 🐳 STEP 8: Docker Deployment (Optional)

If you want to deploy with Docker:

### 8.1 Build Docker Image

```bash
# Build the image
docker build -t voice-cloning-api .

# This takes 5-10 minutes
```

### 8.2 Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f voice-api

# Stop services
docker-compose down
```

### 8.3 Access Dockerized API

Same URLs as before:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/api/v1/docs`
- Health: `http://localhost:8000/api/v1/health`

---

## 🔧 Troubleshooting

### Issue 1: "Module not found" errors

```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r api/requirements.txt
```

### Issue 2: "FFmpeg not found"

```bash
# Test FFmpeg
ffmpeg -version

# If not found, install it (see Prerequisites section)
# Then restart your terminal
```

### Issue 3: API won't start

```bash
# Check if port 8000 is already in use
# Windows:
netstat -ano | findstr :8000

# macOS/Linux:
lsof -i :8000

# Kill the process or use different port:
python -m uvicorn api.main:app --port 8001
```

### Issue 4: Slow synthesis (>5 seconds)

```bash
# This is normal on CPU
# For faster performance:
# 1. Use a machine with NVIDIA GPU
# 2. Install CUDA version of PyTorch
# 3. Set TTS_DEVICE=cuda in .env file

# Check current device:
curl http://localhost:8000/api/v1/health | grep device
```

### Issue 5: Poor audio quality

- Check your voice sample quality
- Try a different voice sample (clearer audio)
- Disable telephony filter for testing:
  ```json
  {
    "telephony_format": false
  }
  ```

### Issue 6: Port 8000 already in use

```bash
# Option A: Use different port
python -m uvicorn api.main:app --port 8001

# Option B: Kill process using port 8000
# Find process ID
lsof -ti:8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill it
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

---

## 📚 Next Steps

### 1. Read Full Documentation

- **API Reference:** [API_README.md](API_README.md)
- **Implementation Summary:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

### 2. Integrate with AI Phone Platform

- **Vapi.ai:** See `api/integrations/vapi_integration.py`
- **Bland AI:** See `api/integrations/bland_ai_integration.py`
- **Retell AI:** See `api/integrations/retell_ai_integration.py`

### 3. Customize Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
code .env

# Key settings:
# - TTS_DEVICE=cuda  # Use GPU if available
# - ADD_NATURAL_PAUSES=true
# - ADD_BREATHING=true
# - TELEPHONY_SAMPLE_RATE=8000
```

### 4. Deploy to Production

```bash
# Using Docker (recommended)
docker-compose up -d

# Or deploy to cloud:
# - AWS EC2 with GPU
# - Google Cloud with T4 GPU
# - Azure with GPU VM
```

---

## ✅ Verification Checklist

Before moving to production, verify:

- [ ] ✅ API starts without errors
- [ ] ✅ Health check returns "healthy"
- [ ] ✅ Can list voices
- [ ] ✅ Can synthesize speech
- [ ] ✅ Audio plays correctly
- [ ] ✅ Latency is acceptable (<2s on CPU, <1s on GPU)
- [ ] ✅ Can upload custom voice
- [ ] ✅ Custom voice works
- [ ] ✅ Documentation accessible
- [ ] ✅ Metrics endpoint works

---

## 🎉 Success!

If you've completed all steps, you now have:

✅ **Working Voice Cloning API** running locally
✅ **Tested synthesis** with sample voices
✅ **Interactive API documentation** accessible
✅ **Custom voice** capability verified
✅ **Ready for integration** with AI phone platforms

---

## 💬 Need Help?

- **API Docs:** http://localhost:8000/api/v1/docs
- **Full Guide:** [API_README.md](API_README.md)
- **GitHub Issues:** Open an issue if you encounter problems

---

## 🚀 Quick Command Reference

```bash
# Activate environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Run API
python -m uvicorn api.main:app --reload

# Test health
curl http://localhost:8000/api/v1/health

# List voices
curl http://localhost:8000/api/v1/voices

# Synthesize speech
curl -X POST http://localhost:8000/api/v1/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world","voice_id":"sample_1320_00000"}'

# View documentation
open http://localhost:8000/api/v1/docs  # macOS
xdg-open http://localhost:8000/api/v1/docs  # Linux
start http://localhost:8000/api/v1/docs  # Windows
```

---

**Enjoy your Voice Cloning API!** 🎙️

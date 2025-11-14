# AI Video Processor - Installation & Usage Guide

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg installed and accessible in PATH
- At least 4GB RAM (8GB+ recommended for longer videos)
- Optional: CUDA-capable GPU for faster processing

### Installation

1. **Install System Dependencies**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y ffmpeg python3-pip python3-dev

# macOS
brew install ffmpeg python3

# Windows
# Download FFmpeg from https://ffmpeg.org/download.html
# Add to PATH
```

2. **Install Python Dependencies**

```bash
cd video-editor-app/ai-processor
pip install -r requirements.txt
```

This will install:
- **PySceneDetect**: Advanced scene detection
- **MoviePy**: Professional video editing and transitions
- **Librosa**: Music analysis (beats, onsets, tempo)
- **OpenCV**: Computer vision and video processing
- **Flask**: API server
- And all other required dependencies

3. **Verify Installation**

```bash
python -c "import scenedetect, moviepy, librosa; print('✓ All dependencies installed')"
```

---

## 🎬 Usage

### Option 1: Run as Flask API Server

```bash
cd video-editor-app/ai-processor
python app.py
```

The server will start on `http://localhost:5000`

**Available Endpoints:**

1. **Health Check**
```bash
curl http://localhost:5000/health
```

2. **Analyze Files Only** (backward compatible)
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {"path": "/path/to/video1.mp4", "mimetype": "video/mp4"},
      {"path": "/path/to/image.jpg", "mimetype": "image/jpeg"}
    ],
    "music": {"path": "/path/to/music.mp3"},
    "settings": {}
  }'
```

3. **Full Video Processing** (NEW - with beat sync & MoviePy)
```bash
curl -X POST http://localhost:5000/process_video \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {"path": "/path/to/video1.mp4", "mimetype": "video/mp4"},
      {"path": "/path/to/video2.mp4", "mimetype": "video/mp4"}
    ],
    "music": {"path": "/path/to/music.mp3"},
    "settings": {
      "videoDuration": "auto",
      "videoQuality": "1080p",
      "transitionStyle": "adaptive",
      "enableColorGrading": true,
      "enableStabilization": false
    },
    "outputPath": "/path/to/output.mp4"
  }'
```

### Option 2: Command-Line Interface

```bash
python video_processor.py \
  --files '[{"path": "video1.mp4", "mimetype": "video/mp4"}]' \
  --music /path/to/music.mp3 \
  --settings '{"videoQuality": "1080p", "transitionStyle": "energetic"}' \
  --output output.mp4
```

### Option 3: Python API

```python
from video_processor import VideoProcessor

# Initialize processor
processor = VideoProcessor(use_moviepy=True)

# Process video
result = processor.process(
    files=[
        {'path': 'video1.mp4', 'mimetype': 'video/mp4'},
        {'path': 'video2.mp4', 'mimetype': 'video/mp4'}
    ],
    music={'path': 'music.mp3'},
    settings={
        'videoDuration': 'auto',  # or specific duration in seconds
        'videoQuality': '1080p',   # '720p', '1080p', or '4k'
        'transitionStyle': 'adaptive',  # 'adaptive', 'energetic', or 'smooth'
        'enableColorGrading': True,
        'enableStabilization': False
    },
    output_path='output.mp4'
)

print(f"Video created: {result['output_path']}")
```

---

## ⚙️ Configuration Options

### Settings Dictionary

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `videoDuration` | string/float | `'auto'` | Target video duration. `'auto'` matches music length, or specify seconds |
| `videoQuality` | string | `'1080p'` | Output quality: `'720p'`, `'1080p'`, or `'4k'` |
| `transitionStyle` | string | `'adaptive'` | Transition style: `'adaptive'` (music-based), `'energetic'`, or `'smooth'` |
| `enableColorGrading` | boolean | `true` | Apply color enhancement |
| `enableStabilization` | boolean | `false` | Enable video stabilization (slower) |

### Transition Styles

- **`adaptive`** (Recommended): Automatically adjusts transitions based on music energy and mood
  - High energy music → fast wipes (0.2-0.3s)
  - Low energy music → smooth crossfades (0.8-1.0s)
  - Onsets get punchy transitions, downbeats get smoother ones

- **`energetic`**: Fast, punchy transitions (0.2s wipes) for high-energy content

- **`smooth`**: Longer, smooth crossfades (0.8s) for cinematic feel

---

## 🎵 Music Analysis Features

The music analyzer uses **Librosa** to extract:

- **Tempo (BPM)**: Beats per minute
- **Beats**: Precise beat timestamps with strength indicators
  - Downbeats (every 4th beat) marked as strong
  - Regular beats marked as medium strength
- **Onsets**: Impactful moments (drum hits, sudden changes)
  - Used for punchy cut placements
  - Weighted by intensity
- **Energy**: Overall energy level (0-1)
- **Mood**: Estimated mood (`energetic`, `calm`, `dynamic`, `neutral`)
- **Spectral Features**: Brightness, percussiveness

### Beat Synchronization

The `BeatSynchronizer` aligns video cuts and transitions to music:

1. **Strong Sync Points**: Combines onsets + downbeats
2. **Clip Alignment**: Places clips to start/end on sync points
3. **Transition Timing**: Transitions occur precisely on beats
4. **Duration Adjustment**: Clips sized to fit between beats

**Example Timeline:**
```
Music:    |--ONSET--|--beat--|--ONSET--|--beat--|--DOWNBEAT--|
Video:    [Clip 1................][Clip 2................]
Trans:                       ^wipe^                    ^fade^
```

---

## 🎬 Scene Detection Features

Uses **PySceneDetect** for superior scene detection:

### Detection Methods

1. **ContentDetector** (Primary)
   - Detects fast cuts based on frame content changes
   - Threshold: 27.0 (optimized for most videos)
   - Filters scenes < 0.5s

2. **AdaptiveDetector** (Fallback)
   - Detects gradual transitions (fades, dissolves)
   - Auto-enabled if < 3 scenes found with ContentDetector
   - Adapts to video characteristics

### Scene Quality Scoring

Scenes are scored based on duration:
- **2-5 seconds**: Score 1.0 (optimal)
- **1-2 seconds**: Score 0.8 (good)
- **5-8 seconds**: Score 0.9 (good but longer)
- **< 1 second**: Score 0.5 (too short)
- **> 8 seconds**: Score 0.7 (too long)

High-quality scenes are prioritized in the final edit.

---

## 🎨 MoviePy Rendering Features

Professional rendering with **MoviePy**:

### Transitions

- **Crossfade**: Smooth opacity blend between clips
- **Dissolve**: Similar to crossfade with slight variations
- **Wipe**: Directional transition (left-to-right, etc.)
- **Slide**: Sliding transition
- **Zoom**: Zoom in/out effect

### Video Processing

- **Scaling**: Maintains aspect ratio while fitting target resolution
- **Padding**: Black bars added if needed to match resolution
- **Color Grading**: Subtle contrast and saturation enhancement
- **FPS Normalization**: All clips converted to consistent FPS

### Audio Mixing

- **Music Background**: Automatically trimmed to video length
- **Fade Out**: 1-second fade out at end
- **Audio Codec**: AAC at 192kbps

---

## 📊 Logging

Detailed logging at every step:

```
🎬 STARTING AUTOMATED VIDEO EDITING
============================================================

📊 STEP 1: ANALYZING FILES
------------------------------------------------------------
🎬 Analyzing video: video1.mp4
  Duration: 30.50s, FPS: 29.97, Frames: 914
  🔍 Running PySceneDetect ContentDetector...
  ✓ Detected 12 high-quality scenes
  Detected 12 scenes using pyscenedetect method
  Average scene quality: 0.85

🎵 STEP 2: ANALYZING MUSIC
------------------------------------------------------------
🎵 Analyzing music: song.mp3
  Duration: 180.00s
  🔍 Running advanced Librosa analysis...
  Sample rate: 22050 Hz, Samples: 3969000
  🥁 Detecting beats...
  Detected 354 beats at 120.5 BPM
  💥 Detecting onsets (impactful moments)...
  Detected 87 onsets
  ✓ Analysis complete: 354 beats, 87 onsets

📝 STEP 3: GENERATING EDIT PLAN
------------------------------------------------------------
Generating edit plan...
  Target duration: 180.0s
🎵 Synchronizing clips to music beats...
  Music: 120.5 BPM, 354 beats, 87 onsets
  Clips: 3 clips to sync
  Using 95 sync points (onsets + strong beats)
    Clip 1: 0.50s - 60.20s (59.70s) [onset]
    Clip 2: 60.20s - 120.80s (60.60s) [downbeat]
    Clip 3: 120.80s - 180.00s (59.20s) [onset]
  ✓ Synchronized 3 clips
  🎬 Suggesting transitions (style: adaptive)...
  ✓ Generated 2 transitions

✓ Edit plan generated:
  Clips: 3
  Transitions: 2
  Resolution: 1920x1080

🎨 STEP 4: RENDERING VIDEO
------------------------------------------------------------
Using MoviePy renderer (professional mode)
🎬 Starting MoviePy render...
  Output: output.mp4
  Resolution: 1920x1080 @ 30fps
  Clips: 3, Transitions: 2
  📹 Loading and processing clips...
    Loading clip 1/3: video1.mp4
    Loading clip 2/3: video2.mp4
    Loading clip 3/3: video3.mp4
  ✨ Applying transitions...
      Clip 1 -> 2: dissolve (0.5s)
      Clip 2 -> 3: wipe (0.3s)
    Concatenating with crossfade (0.4s)...
  🎵 Adding background music...
  🎨 Rendering final video...
  Codec: libx264, Bitrate: 8000k
  ✓ Render complete: output.mp4

============================================================
✅ VIDEO PROCESSING COMPLETE
============================================================
📹 Output: output.mp4
```

---

## 🧪 Testing

### Create Test Script

```python
# test_processor.py
from video_processor import VideoProcessor
import time

processor = VideoProcessor()

# Test 1: Short video (< 30s)
print("Test 1: Short video")
start = time.time()
result = processor.process(
    files=[{'path': 'short.mp4', 'mimetype': 'video/mp4'}],
    music={'path': 'music.mp3'},
    settings={'videoDuration': 30},
    output_path='test_short.mp4'
)
print(f"✓ Completed in {time.time() - start:.2f}s")

# Test 2: Long video (> 2min)
print("\nTest 2: Long video")
start = time.time()
result = processor.process(
    files=[
        {'path': 'long1.mp4', 'mimetype': 'video/mp4'},
        {'path': 'long2.mp4', 'mimetype': 'video/mp4'},
        {'path': 'long3.mp4', 'mimetype': 'video/mp4'}
    ],
    music={'path': 'music.mp3'},
    settings={'videoDuration': 'auto', 'transitionStyle': 'energetic'},
    output_path='test_long.mp4'
)
print(f"✓ Completed in {time.time() - start:.2f}s")
```

```bash
python test_processor.py
```

---

## 🔧 Troubleshooting

### MoviePy Not Found

```
❌ MoviePy not available - install with: pip install moviepy
```

**Solution:**
```bash
pip install moviepy imageio imageio-ffmpeg
```

### Librosa Not Found

```
⚠ Librosa not available - using basic analysis
```

**Solution:**
```bash
pip install librosa soundfile numba
```

### PySceneDetect Not Found

```
⚠ PySceneDetect not available - using fallback histogram method
```

**Solution:**
```bash
pip install scenedetect[opencv]
```

### FFmpeg Not in PATH

```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**Solution:**
- Ensure FFmpeg is installed
- Add FFmpeg to system PATH
- On Linux: `sudo apt-get install ffmpeg`
- On macOS: `brew install ffmpeg`
- On Windows: Download and add to PATH

### Out of Memory

```
MemoryError: Unable to allocate...
```

**Solutions:**
- Reduce video quality: Use `'720p'` instead of `'1080p'`
- Process fewer clips at once
- Use smaller `videoDuration`
- Disable `enableStabilization`

---

## 📈 Performance Tips

1. **Use SSD**: Store input/output files on SSD for faster I/O
2. **Reduce Quality for Testing**: Use `'720p'` during development
3. **Disable Stabilization**: Only enable for shaky footage
4. **Limit Analysis Duration**: Music analyzer only analyzes first 90s
5. **GPU Acceleration**: MoviePy can use GPU for encoding (requires proper setup)

---

## 🌟 Best Practices

### For Best Results

1. **High-Quality Input**: Use 1080p+ source videos
2. **Matching Frame Rates**: Source videos with similar FPS
3. **Music with Clear Beats**: Electronic, hip-hop, or pop music works best
4. **Variety in Clips**: Mix of different scenes/angles
5. **Appropriate Duration**: 30-180s videos work best

### Recommended Settings by Use Case

**Social Media (Instagram/TikTok):**
```python
{
    'videoDuration': 30,
    'videoQuality': '1080p',
    'transitionStyle': 'energetic',
    'enableColorGrading': True
}
```

**Cinematic Montage:**
```python
{
    'videoDuration': 'auto',
    'videoQuality': '4k',
    'transitionStyle': 'smooth',
    'enableColorGrading': True,
    'enableStabilization': True
}
```

**Fast-Paced Action:**
```python
{
    'videoDuration': 60,
    'videoQuality': '1080p',
    'transitionStyle': 'energetic',
    'enableColorGrading': False
}
```

---

## 📝 API Reference

See `video_processor.py`, `beat_sync.py`, and `moviepy_renderer.py` for detailed API documentation.

---

## 🤝 Support

For issues or questions:
- Check logs for detailed error messages
- Verify all dependencies are installed
- Ensure FFmpeg is accessible
- Test with shorter videos first

---

## 📄 License

MIT License - See LICENSE file for details

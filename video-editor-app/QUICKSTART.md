# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Check

```bash
node --version    # Should be >= 18
python3 --version # Should be >= 3.10
ffmpeg -version   # Should be installed
```

If any are missing, see [INSTALL.md](INSTALL.md) for installation instructions.

## Option 1: Automated Start (Recommended)

### Linux/macOS
```bash
./start.sh
```

### Windows
```bash
start.bat
```

Open http://localhost:3000 in your browser!

## Option 2: Docker (Easiest)

```bash
docker-compose up --build
```

Open http://localhost:3000 in your browser!

## Option 3: Manual Start

### Terminal 1 - AI Processor
```bash
cd ai-processor
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Terminal 2 - Backend
```bash
cd backend
npm install
node server.js
```

Open http://localhost:3000 in your browser!

## First Video

1. **Upload** files: Drag & drop photos/videos
2. **Add music** (optional): Click music button
3. **Configure**: Choose quality and style
4. **Generate**: Click the generate button
5. **Download**: Your video is ready!

## Need Help?

- 📖 Full docs: [README.md](README.md)
- 🔧 Installation: [INSTALL.md](INSTALL.md)
- 🔌 API docs: [API.md](API.md)
- 🐛 Issues: Open a GitHub issue

## Common Issues

### "FFmpeg not found"
Install FFmpeg: https://ffmpeg.org/download.html

### "Port already in use"
Kill existing process:
```bash
# Linux/Mac
lsof -ti:3000 | xargs kill -9

# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### "Module not found"
```bash
# Backend
cd backend && npm install

# AI Processor
cd ai-processor && pip install -r requirements.txt
```

## What's Next?

- Read [README.md](README.md) for full features
- Check [API.md](API.md) to integrate in your app
- Deploy to production: See [INSTALL.md](INSTALL.md) for VPS setup

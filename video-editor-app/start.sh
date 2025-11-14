#!/bin/bash

# AI Video Editor - Start Script

echo "🎬 Starting AI Video Editor..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}❌ FFmpeg is not installed!${NC}"
    echo "Please install FFmpeg first:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/download.html"
    exit 1
fi

echo -e "${GREEN}✓ FFmpeg found${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed!${NC}"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓ Node.js found${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python is not installed!${NC}"
    echo "Please install Python 3.10+ from https://python.org/"
    exit 1
fi

echo -e "${GREEN}✓ Python found${NC}"

# Install backend dependencies
if [ ! -d "backend/node_modules" ]; then
    echo -e "${BLUE}📦 Installing backend dependencies...${NC}"
    cd backend
    npm install
    cd ..
fi

# Setup Python virtual environment
if [ ! -d "ai-processor/venv" ]; then
    echo -e "${BLUE}🐍 Setting up Python virtual environment...${NC}"
    cd ai-processor
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    cd ..
fi

# Create necessary directories
mkdir -p uploads outputs temp

# Start services
echo -e "${BLUE}🚀 Starting services...${NC}"

# Start AI Processor in background
echo -e "${BLUE}Starting AI Processor...${NC}"
cd ai-processor
source venv/bin/activate
python app.py &
AI_PID=$!
cd ..

# Wait a bit for AI service to start
sleep 3

# Start Backend
echo -e "${BLUE}Starting Backend...${NC}"
cd backend
node server.js &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 2

echo ""
echo -e "${GREEN}✅ Application started successfully!${NC}"
echo ""
echo -e "${BLUE}📱 Access the application at:${NC}"
echo "   http://localhost:3000"
echo ""
echo -e "${BLUE}📊 Service status:${NC}"
echo "   Backend PID: $BACKEND_PID"
echo "   AI Processor PID: $AI_PID"
echo ""
echo -e "${BLUE}To stop the application:${NC}"
echo "   Press Ctrl+C or run: kill $BACKEND_PID $AI_PID"
echo ""

# Trap Ctrl+C to cleanup
trap "echo -e '\n${RED}Stopping services...${NC}'; kill $BACKEND_PID $AI_PID; exit" INT

# Wait for processes
wait

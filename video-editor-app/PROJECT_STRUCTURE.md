# Project Structure

Complete overview of the AI Video Editor project structure.

```
video-editor-app/
│
├── frontend/                          # Frontend web application
│   ├── index.html                     # Main HTML page
│   ├── css/
│   │   └── style.css                  # Styles and animations
│   └── js/
│       └── app.js                     # Frontend logic and API calls
│
├── backend/                           # Node.js/Express backend
│   ├── server.js                      # Main server file
│   ├── package.json                   # Node.js dependencies
│   ├── Dockerfile                     # Docker configuration
│   ├── routes/                        # API routes (empty, integrated in server.js)
│   └── services/                      # Business logic services (empty, integrated in server.js)
│
├── ai-processor/                      # Python AI microservice
│   ├── app.py                         # Flask application
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile                     # Docker configuration
│   ├── test_analyzers.py              # Test script for analyzers
│   └── analyzers/                     # AI analysis modules
│       ├── quality.py                 # Quality analyzer (blur, exposure, etc.)
│       ├── scene.py                   # Scene detection (changes, cuts)
│       ├── content.py                 # Content analyzer (faces, objects)
│       └── music.py                   # Music analyzer (BPM, beats, energy)
│
├── uploads/                           # Uploaded files directory
│   └── .gitkeep                       # Keep directory in git
│
├── outputs/                           # Generated videos directory
│   └── .gitkeep                       # Keep directory in git
│
├── temp/                              # Temporary processing files
│   └── .gitkeep                       # Keep directory in git
│
├── docker-compose.yml                 # Docker Compose configuration
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── nginx.conf.example                 # Nginx configuration for production
│
├── start.sh                           # Start script for Linux/macOS
├── start.bat                          # Start script for Windows
│
├── README.md                          # Main documentation
├── QUICKSTART.md                      # Quick start guide
├── INSTALL.md                         # Detailed installation guide
├── API.md                             # API documentation
├── PROJECT_STRUCTURE.md               # This file
└── LICENSE                            # MIT License

```

## File Descriptions

### Frontend Files

**index.html**
- Main HTML page with complete UI structure
- Upload zone, file management, settings, progress tracking
- Responsive design with modern UI components

**style.css**
- Complete styling with dark theme
- Animations and transitions
- Responsive layout for mobile/desktop
- Custom components (cards, buttons, progress bars)

**app.js**
- Frontend application logic
- File upload and drag & drop handling
- Communication with backend API
- Progress polling and status updates
- Video preview and download

### Backend Files

**server.js** (Node.js/Express)
- HTTP server on port 3000
- File upload handling with Multer
- Job management and status tracking
- Communication with AI processor
- FFmpeg video rendering
- API endpoints:
  - `POST /api/upload` - Upload files
  - `GET /api/status/:jobId` - Get job status

**package.json**
- Dependencies: express, cors, multer, uuid, axios
- Scripts: start, dev

**Dockerfile**
- Based on Node.js 18 Alpine
- Includes FFmpeg
- Production-ready configuration

### AI Processor Files

**app.py** (Flask)
- Flask web server on port 5000
- Coordinates all analyzers
- API endpoints:
  - `GET /health` - Health check
  - `POST /analyze` - Analyze files

**quality.py**
- Image/video quality analysis
- Blur detection (Laplacian variance)
- Brightness and contrast analysis
- Exposure detection
- Motion detection for videos

**scene.py**
- Scene change detection
- Histogram comparison
- Optimal cut point suggestions
- Motion intensity analysis
- Optical flow calculations

**content.py**
- Face detection (Haar Cascades)
- Composition analysis (rule of thirds)
- Dominant color extraction (K-means)
- Interest score calculation
- Text region detection

**music.py**
- Audio duration extraction (FFprobe)
- BPM detection (Librosa)
- Beat tracking and timestamps
- Energy and brightness analysis
- Music mood estimation

**test_analyzers.py**
- Standalone testing script
- Test individual analyzers
- Export results to JSON
- Usage: `python test_analyzers.py <file>`

**requirements.txt**
- Dependencies: Flask, OpenCV, NumPy, Librosa, SciPy, etc.

**Dockerfile**
- Based on Python 3.10 Slim
- Includes system dependencies
- Installs all Python packages

### Configuration Files

**docker-compose.yml**
- Multi-container setup
- Backend + AI Processor services
- Shared volumes for uploads/outputs
- Network configuration

**.env.example**
- Environment variables template
- Port configuration
- File size limits
- Service URLs

**.gitignore**
- Node.js, Python, and system files
- Uploads, outputs, temp directories
- Environment and IDE files

**nginx.conf.example**
- Production Nginx configuration
- SSL/HTTPS setup
- Proxy to backend
- Rate limiting
- File upload size limits

### Scripts

**start.sh** (Linux/macOS)
- Check prerequisites
- Install dependencies
- Start both services
- Open browser

**start.bat** (Windows)
- Check prerequisites
- Install dependencies
- Start both services in separate windows
- Open browser

### Documentation

**README.md**
- Complete project overview
- Features list
- Installation instructions
- Usage guide
- Deployment instructions
- Troubleshooting

**QUICKSTART.md**
- 5-minute quick start
- Essential commands
- Common issues
- Next steps

**INSTALL.md**
- Detailed installation guide
- Prerequisites for each platform
- Step-by-step setup
- Production deployment
- VPS configuration

**API.md**
- Complete API reference
- Endpoint documentation
- Request/response examples
- Error handling
- Rate limiting

**LICENSE**
- MIT License
- Open source and free to use

## Data Flow

1. **User uploads files** → Frontend
2. **Files sent to backend** → `POST /api/upload`
3. **Backend saves files** → uploads/ directory
4. **Backend requests analysis** → AI Processor
5. **AI analyzes each file** → quality, content, scenes, music
6. **AI returns analysis** → Backend
7. **Backend generates edit plan** → Duration, transitions, filters
8. **FFmpeg renders video** → outputs/ directory
9. **Backend updates status** → Progress tracking
10. **Frontend polls status** → `GET /api/status/:jobId`
11. **User downloads video** → Frontend

## Technology Stack

### Frontend
- HTML5, CSS3, JavaScript (Vanilla)
- Sortable.js for drag & drop
- Fetch API for HTTP requests

### Backend
- Node.js 18+
- Express 4.x
- Multer for file uploads
- Axios for HTTP client
- UUID for unique IDs

### AI Processor
- Python 3.10+
- Flask for web framework
- OpenCV for computer vision
- Librosa for audio analysis
- NumPy for numerical computing
- SciPy for scientific functions

### Video Processing
- FFmpeg 4.4+
- H.264 encoding
- Multiple filters (scale, stabilize, color grade)
- Complex filter graphs

### Deployment
- Docker & Docker Compose
- Nginx for reverse proxy
- Let's Encrypt for SSL
- Systemd for service management

## Development Workflow

### Local Development

1. Start AI Processor:
   ```bash
   cd ai-processor
   source venv/bin/activate
   python app.py
   ```

2. Start Backend:
   ```bash
   cd backend
   npm run dev  # Uses nodemon for auto-reload
   ```

3. Frontend: Open http://localhost:3000

### Testing

- Backend: Manual testing with curl or Postman
- AI Processor: `python test_analyzers.py <file>`
- Frontend: Browser testing with developer tools

### Debugging

- Backend logs: Console output
- AI Processor logs: Console output
- FFmpeg logs: Captured in stderr
- Browser logs: Developer console

## Extending the Application

### Add New Analyzer

1. Create `ai-processor/analyzers/new_analyzer.py`
2. Implement analysis logic
3. Import in `app.py`
4. Call in analyze endpoint

### Add New API Endpoint

1. Add route in `backend/server.js`
2. Implement handler function
3. Update API.md documentation

### Add New Frontend Feature

1. Update HTML in `index.html`
2. Add styles in `style.css`
3. Implement logic in `app.js`

### Add New FFmpeg Filter

1. Locate `buildFFmpegCommand()` in `server.js`
2. Add filter to filter_complex
3. Test with sample videos

## Performance Considerations

### Bottlenecks
- Video rendering (CPU intensive)
- AI analysis (CPU intensive)
- Large file uploads (Network/Disk I/O)

### Optimizations
- Process jobs in queue (Bull/Redis)
- Cache analysis results
- Use GPU acceleration for FFmpeg
- Implement CDN for outputs
- Optimize AI models
- Reduce video resolution for preview

## Security Notes

- No authentication (add for production)
- File type validation (basic)
- No input sanitization (add for production)
- No rate limiting (add for production)
- No CSRF protection (add for production)

See nginx.conf.example for production hardening.

## Future Enhancements

- [ ] User accounts and authentication
- [ ] Job queue with Bull/Redis
- [ ] Real-time WebSocket progress
- [ ] Video preview before download
- [ ] Custom transition effects
- [ ] Template library
- [ ] Cloud storage integration
- [ ] Mobile app
- [ ] Collaborative editing
- [ ] AI-powered music generation

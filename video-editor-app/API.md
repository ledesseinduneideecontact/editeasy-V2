# API Documentation

## Base URL

- **Development**: `http://localhost:3000/api`
- **Production**: `https://your-domain.com/api`

## Authentication

Currently, no authentication is required. For production use, consider adding authentication.

## Endpoints

### 1. Upload Files and Start Processing

**Endpoint**: `POST /api/upload`

**Description**: Upload media files (photos/videos) and optional music, then start the automatic video editing process.

**Content-Type**: `multipart/form-data`

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| files[] | File[] | Yes | Array of image and video files |
| music | File | No | Background music file (MP3, WAV, etc.) |
| settings | JSON String | Yes | Video generation settings |

**Settings Object**:

```json
{
  "videoDuration": "60",              // "auto" or duration in seconds
  "transitionStyle": "auto",          // "auto", "smooth", "dynamic", "mixed"
  "videoQuality": "1080p",            // "720p", "1080p", "4k"
  "musicSync": "high",                // "low", "medium", "high"
  "enableStabilization": true,        // boolean
  "enableColorGrading": true          // boolean
}
```

**Example Request (JavaScript)**:

```javascript
const formData = new FormData();

// Add files
files.forEach(file => {
  formData.append('files', file);
});

// Add music (optional)
if (musicFile) {
  formData.append('music', musicFile);
}

// Add settings
const settings = {
  videoDuration: "60",
  transitionStyle: "auto",
  videoQuality: "1080p",
  musicSync: "high",
  enableStabilization: true,
  enableColorGrading: true
};
formData.append('settings', JSON.stringify(settings));

// Send request
const response = await fetch('http://localhost:3000/api/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log('Job ID:', data.jobId);
```

**Example Request (cURL)**:

```bash
curl -X POST http://localhost:3000/api/upload \
  -F "files=@photo1.jpg" \
  -F "files=@photo2.jpg" \
  -F "files=@video1.mp4" \
  -F "music=@song.mp3" \
  -F 'settings={"videoDuration":"60","transitionStyle":"auto","videoQuality":"1080p","musicSync":"high","enableStabilization":true,"enableColorGrading":true}'
```

**Success Response (200 OK)**:

```json
{
  "jobId": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Upload réussi"
}
```

**Error Responses**:

- **400 Bad Request**: Invalid file type or missing parameters
```json
{
  "error": "Type de fichier non supporté"
}
```

- **413 Payload Too Large**: File size exceeds limit
```json
{
  "error": "File too large"
}
```

- **500 Internal Server Error**: Server error
```json
{
  "error": "Internal server error message"
}
```

---

### 2. Check Job Status

**Endpoint**: `GET /api/status/:jobId`

**Description**: Get the current status and progress of a video generation job.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| jobId | String (UUID) | Yes | Job ID returned from upload endpoint |

**Example Request (JavaScript)**:

```javascript
const jobId = '550e8400-e29b-41d4-a716-446655440000';
const response = await fetch(`http://localhost:3000/api/status/${jobId}`);
const status = await response.json();

if (status.status === 'completed') {
  console.log('Video ready:', status.videoUrl);
}
```

**Example Request (cURL)**:

```bash
curl http://localhost:3000/api/status/550e8400-e29b-41d4-a716-446655440000
```

**Response (Processing)**:

```json
{
  "status": "processing",
  "progress": 45,
  "message": "Montage vidéo en cours...",
  "steps": [
    {
      "text": "Upload des fichiers",
      "completed": true
    },
    {
      "text": "Analyse IA",
      "completed": true
    },
    {
      "text": "Plan de montage",
      "completed": true
    },
    {
      "text": "Rendu vidéo",
      "active": true
    }
  ]
}
```

**Response (Completed)**:

```json
{
  "status": "completed",
  "progress": 100,
  "message": "Vidéo prête !",
  "videoUrl": "/outputs/video-550e8400-e29b-41d4-a716-446655440000.mp4",
  "steps": [
    {
      "text": "Upload des fichiers",
      "completed": true
    },
    {
      "text": "Analyse IA",
      "completed": true
    },
    {
      "text": "Plan de montage",
      "completed": true
    },
    {
      "text": "Rendu vidéo",
      "completed": true
    }
  ]
}
```

**Response (Failed)**:

```json
{
  "status": "failed",
  "progress": 50,
  "message": "Erreur lors du traitement",
  "error": "FFmpeg exited with code 1: Error message...",
  "steps": [...]
}
```

**Error Responses**:

- **404 Not Found**: Job ID not found
```json
{
  "error": "Job not found"
}
```

---

## Status Polling

To monitor job progress, poll the status endpoint every 2-3 seconds:

```javascript
async function pollStatus(jobId) {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/status/${jobId}`);
    const data = await response.json();

    console.log(`Progress: ${data.progress}% - ${data.message}`);

    if (data.status === 'completed') {
      clearInterval(interval);
      console.log('Video ready!', data.videoUrl);
      // Download or display video
    } else if (data.status === 'failed') {
      clearInterval(interval);
      console.error('Processing failed:', data.error);
    }
  }, 2000); // Poll every 2 seconds
}
```

---

## AI Processor Endpoints

The AI processor runs on port 5000 and provides analysis services.

### Health Check

**Endpoint**: `GET /health`

**Description**: Check if AI processor is running.

**Response**:

```json
{
  "status": "healthy"
}
```

### Analyze Files

**Endpoint**: `POST /analyze`

**Description**: Analyze media files for quality, content, scenes, and music.

**Request Body**:

```json
{
  "files": [
    {
      "path": "/path/to/file.jpg",
      "mimetype": "image/jpeg",
      "size": 1024000
    }
  ],
  "music": {
    "path": "/path/to/music.mp3"
  },
  "settings": {}
}
```

**Response**:

```json
{
  "filesAnalysis": [
    {
      "path": "/path/to/file.jpg",
      "type": "image",
      "quality": 0.85,
      "duration": 3,
      "hasFaces": true,
      "faces": [
        {
          "x": 0.25,
          "y": 0.3,
          "width": 0.15,
          "height": 0.2,
          "confidence": 0.8
        }
      ],
      "composition": {
        "compositionScore": 0.75
      },
      "interestScore": 0.8
    }
  ],
  "musicAnalysis": {
    "duration": 180,
    "bpm": 120,
    "energy": 0.7,
    "mood": "energetic",
    "beats": [
      { "time": 0.5, "strength": 1.0 },
      { "time": 1.0, "strength": 0.5 }
    ]
  }
}
```

---

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Job or resource not found |
| 413 | Payload Too Large - File size exceeds limit |
| 500 | Internal Server Error |

---

## Rate Limiting

Consider implementing rate limiting in production:

- Upload endpoint: 5 requests per minute per IP
- Status endpoint: 30 requests per minute per IP

See `nginx.conf.example` for configuration.

---

## File Size Limits

Default limits (configurable in `.env`):

- **Max file size**: 500MB per file
- **Max total files**: 100 files per upload
- **Max total size**: Limited by disk space

---

## Supported File Formats

### Images
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

### Videos
- MP4 (.mp4)
- MOV (.mov)
- AVI (.avi)
- MKV (.mkv)
- WebM (.webm)
- FLV (.flv)

### Audio
- MP3 (.mp3)
- WAV (.wav)
- OGG (.ogg)
- M4A (.m4a)
- FLAC (.flac)

---

## Error Handling

All errors return a JSON response with an `error` field:

```json
{
  "error": "Description of the error"
}
```

Client should handle:
- Network errors
- Timeout errors (long processing)
- Invalid responses
- Server errors

Example error handling:

```javascript
try {
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Upload failed');
  }

  const data = await response.json();
  // Continue with data.jobId
} catch (error) {
  console.error('Upload error:', error.message);
  // Show error to user
}
```

---

## Examples

### Complete Workflow Example

```javascript
async function generateVideo(files, musicFile, settings) {
  try {
    // 1. Upload files
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    if (musicFile) formData.append('music', musicFile);
    formData.append('settings', JSON.stringify(settings));

    const uploadRes = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });

    if (!uploadRes.ok) throw new Error('Upload failed');

    const { jobId } = await uploadRes.json();
    console.log('Job started:', jobId);

    // 2. Poll for status
    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        try {
          const statusRes = await fetch(`/api/status/${jobId}`);
          const status = await statusRes.json();

          console.log(`${status.progress}%: ${status.message}`);

          if (status.status === 'completed') {
            clearInterval(interval);
            resolve(status.videoUrl);
          } else if (status.status === 'failed') {
            clearInterval(interval);
            reject(new Error(status.error));
          }
        } catch (error) {
          clearInterval(interval);
          reject(error);
        }
      }, 2000);
    });

  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Usage
const videoUrl = await generateVideo(
  myFiles,
  myMusicFile,
  {
    videoDuration: '60',
    transitionStyle: 'auto',
    videoQuality: '1080p',
    musicSync: 'high',
    enableStabilization: true,
    enableColorGrading: true
  }
);

console.log('Video ready:', videoUrl);
```

---

## Security Considerations

For production deployment:

1. **Add authentication**: JWT tokens or session-based auth
2. **Rate limiting**: Prevent abuse
3. **File validation**: Strict MIME type checking
4. **Size limits**: Enforce reasonable limits
5. **CORS**: Configure properly for your domain
6. **HTTPS**: Always use SSL in production
7. **Input sanitization**: Validate all user inputs
8. **Temporary file cleanup**: Regular cleanup of old jobs

---

## Performance Tips

1. **Batch processing**: Process multiple jobs in queue
2. **Caching**: Cache AI analysis results
3. **CDN**: Serve output videos via CDN
4. **Optimization**: Pre-process videos to standard format
5. **Monitoring**: Track processing times and failures

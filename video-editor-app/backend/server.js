const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises;
const multer = require('multer');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));
app.use('/outputs', express.static(path.join(__dirname, '../outputs')));

// Storage configuration
const storage = multer.diskStorage({
    destination: async (req, file, cb) => {
        const uploadDir = path.join(__dirname, '../uploads');
        try {
            await fs.mkdir(uploadDir, { recursive: true });
            cb(null, uploadDir);
        } catch (error) {
            cb(error);
        }
    },
    filename: (req, file, cb) => {
        const uniqueName = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}-${file.originalname}`;
        cb(null, uniqueName);
    }
});

const upload = multer({
    storage,
    limits: { fileSize: 500 * 1024 * 1024 }, // 500MB max
    fileFilter: (req, file, cb) => {
        const allowedTypes = /jpeg|jpg|png|gif|mp4|mov|avi|mkv|webm|mp3|wav|ogg/;
        const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
        const mimetype = allowedTypes.test(file.mimetype);

        if (mimetype && extname) {
            return cb(null, true);
        } else {
            cb(new Error('Type de fichier non supporté'));
        }
    }
});

// Job storage (in production, use Redis or a database)
const jobs = new Map();

// Routes
app.post('/api/upload', upload.fields([
    { name: 'files', maxCount: 100 },
    { name: 'music', maxCount: 1 }
]), async (req, res) => {
    try {
        const jobId = uuidv4();
        const files = req.files['files'] || [];
        const music = req.files['music'] ? req.files['music'][0] : null;
        const settings = JSON.parse(req.body.settings || '{}');

        console.log(`[${jobId}] New job created with ${files.length} files`);

        // Create job
        const job = {
            id: jobId,
            status: 'processing',
            progress: 10,
            message: 'Fichiers uploadés avec succès',
            files: files.map(f => ({
                path: f.path,
                originalName: f.originalname,
                mimetype: f.mimetype,
                size: f.size
            })),
            music: music ? {
                path: music.path,
                originalName: music.originalname
            } : null,
            settings,
            createdAt: Date.now()
        };

        jobs.set(jobId, job);

        // Start processing in background
        processVideo(jobId).catch(error => {
            console.error(`[${jobId}] Error:`, error);
            job.status = 'failed';
            job.error = error.message;
        });

        res.json({ jobId, message: 'Upload réussi' });

    } catch (error) {
        console.error('Upload error:', error);
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/status/:jobId', (req, res) => {
    const { jobId } = req.params;
    const job = jobs.get(jobId);

    if (!job) {
        return res.status(404).json({ error: 'Job not found' });
    }

    const response = {
        status: job.status,
        progress: job.progress,
        message: job.message,
        steps: job.steps || []
    };

    if (job.status === 'completed') {
        response.videoUrl = `/outputs/${path.basename(job.outputPath)}`;
    } else if (job.status === 'failed') {
        response.error = job.error;
    }

    res.json(response);
});

// Process Video
async function processVideo(jobId) {
    const job = jobs.get(jobId);
    const axios = require('axios');

    try {
        // Step 1: Analyze files with AI
        updateJobProgress(job, 20, 'Analyse des fichiers avec IA...', [
            { text: 'Upload des fichiers', completed: true },
            { text: 'Analyse IA en cours', active: true }
        ]);

        const analysisResult = await analyzeWithAI(job);

        // Step 2: Generate edit plan
        updateJobProgress(job, 40, 'Génération du plan de montage...', [
            { text: 'Upload des fichiers', completed: true },
            { text: 'Analyse IA', completed: true },
            { text: 'Plan de montage', active: true }
        ]);

        const editPlan = await generateEditPlan(job, analysisResult);

        // Step 3: Render video with FFmpeg
        updateJobProgress(job, 60, 'Montage vidéo en cours...', [
            { text: 'Upload des fichiers', completed: true },
            { text: 'Analyse IA', completed: true },
            { text: 'Plan de montage', completed: true },
            { text: 'Rendu vidéo', active: true }
        ]);

        const outputPath = await renderVideo(job, editPlan);

        // Step 4: Complete
        updateJobProgress(job, 100, 'Vidéo prête !', [
            { text: 'Upload des fichiers', completed: true },
            { text: 'Analyse IA', completed: true },
            { text: 'Plan de montage', completed: true },
            { text: 'Rendu vidéo', completed: true }
        ]);

        job.status = 'completed';
        job.outputPath = outputPath;

        console.log(`[${jobId}] Job completed successfully`);

    } catch (error) {
        console.error(`[${jobId}] Processing error:`, error);
        job.status = 'failed';
        job.error = error.message;
    }
}

// Analyze with AI
async function analyzeWithAI(job) {
    const axios = require('axios');
    const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:5000';

    try {
        const response = await axios.post(`${AI_SERVICE_URL}/analyze`, {
            files: job.files,
            music: job.music,
            settings: job.settings
        }, {
            timeout: 300000 // 5 minutes
        });

        return response.data;
    } catch (error) {
        console.error('AI analysis error:', error.message);
        // Return default analysis if AI service is not available
        return {
            filesAnalysis: job.files.map(f => ({
                path: f.path,
                quality: 0.8,
                duration: 3,
                type: f.mimetype.startsWith('image') ? 'image' : 'video'
            })),
            musicAnalysis: job.music ? {
                bpm: 120,
                duration: 180,
                beats: []
            } : null
        };
    }
}

// Generate Edit Plan
async function generateEditPlan(job, analysis) {
    const { filesAnalysis, musicAnalysis } = analysis;
    const settings = job.settings;

    // Calculate total duration
    let targetDuration = settings.videoDuration === 'auto' && musicAnalysis
        ? musicAnalysis.duration
        : parseInt(settings.videoDuration) || 60;

    // Calculate duration per file
    const clips = filesAnalysis.map((file, index) => {
        const baseDuration = file.type === 'image' ? 3 : Math.min(file.duration || 5, 8);
        const qualityMultiplier = 0.5 + (file.quality * 0.5);
        const duration = baseDuration * qualityMultiplier;

        return {
            index,
            path: file.path,
            type: file.type,
            duration,
            quality: file.quality,
            startTrim: file.startTrim || 0,
            endTrim: file.endTrim || 0
        };
    });

    // Normalize durations to match target
    const totalDuration = clips.reduce((sum, clip) => sum + clip.duration, 0);
    const scale = targetDuration / totalDuration;
    clips.forEach(clip => {
        clip.duration *= scale;
    });

    // Add transitions
    const transitionDuration = 0.5;
    const transitions = clips.map((clip, index) => {
        if (index === clips.length - 1) return null;

        let type = 'fade';
        if (settings.transitionStyle === 'dynamic') {
            type = 'wipe';
        } else if (settings.transitionStyle === 'mixed') {
            type = index % 2 === 0 ? 'fade' : 'dissolve';
        }

        return {
            type,
            duration: transitionDuration
        };
    }).filter(t => t !== null);

    return {
        clips,
        transitions,
        music: job.music ? job.music.path : null,
        targetDuration,
        resolution: settings.videoQuality === '4k' ? '3840x2160' : settings.videoQuality === '1080p' ? '1920x1080' : '1280x720',
        enableStabilization: settings.enableStabilization,
        enableColorGrading: settings.enableColorGrading
    };
}

// Render Video
async function renderVideo(job, editPlan) {
    const { spawn } = require('child_process');
    const outputDir = path.join(__dirname, '../outputs');
    await fs.mkdir(outputDir, { recursive: true });

    const outputPath = path.join(outputDir, `video-${job.id}.mp4`);

    // Build FFmpeg command
    const ffmpegArgs = buildFFmpegCommand(editPlan, outputPath);

    return new Promise((resolve, reject) => {
        console.log('FFmpeg command:', 'ffmpeg', ffmpegArgs.join(' '));

        const ffmpeg = spawn('ffmpeg', ffmpegArgs);

        let stderr = '';

        ffmpeg.stderr.on('data', (data) => {
            stderr += data.toString();
            // Parse progress if needed
        });

        ffmpeg.on('close', (code) => {
            if (code === 0) {
                resolve(outputPath);
            } else {
                reject(new Error(`FFmpeg exited with code ${code}: ${stderr}`));
            }
        });

        ffmpeg.on('error', (error) => {
            reject(new Error(`FFmpeg error: ${error.message}`));
        });
    });
}

// Build FFmpeg Command
function buildFFmpegCommand(editPlan, outputPath) {
    const args = [];
    const { clips, transitions, music, resolution, enableStabilization, enableColorGrading } = editPlan;

    // Input files
    clips.forEach(clip => {
        args.push('-i', clip.path);
    });

    if (music) {
        args.push('-i', music);
    }

    // Build filter complex
    let filterComplex = '';
    const [width, height] = resolution.split('x');

    // Process each clip
    clips.forEach((clip, index) => {
        let filter = `[${index}:v]`;

        // Scale and pad
        filter += `scale=${width}:${height}:force_original_aspect_ratio=decrease,pad=${width}:${height}:(ow-iw)/2:(oh-ih)/2:black`;

        // Stabilization
        if (enableStabilization && clip.type === 'video') {
            filter += ',deshake';
        }

        // Color grading
        if (enableColorGrading) {
            filter += ',eq=contrast=1.1:brightness=0.05:saturation=1.2';
        }

        // Set duration for images
        if (clip.type === 'image') {
            filter += `,tpad=stop_mode=clone:stop_duration=${clip.duration}`;
        }

        filter += `[v${index}];`;
        filterComplex += filter;
    });

    // Concatenate with transitions
    let concatInput = '';
    clips.forEach((clip, index) => {
        concatInput += `[v${index}]`;
    });

    filterComplex += `${concatInput}concat=n=${clips.length}:v=1:a=0[outv]`;

    args.push('-filter_complex', filterComplex);
    args.push('-map', '[outv]');

    // Audio
    if (music) {
        args.push('-map', `${clips.length}:a`);
        args.push('-shortest');
    }

    // Output options
    args.push('-c:v', 'libx264');
    args.push('-preset', 'medium');
    args.push('-crf', '23');
    args.push('-pix_fmt', 'yuv420p');

    if (music) {
        args.push('-c:a', 'aac');
        args.push('-b:a', '192k');
    }

    args.push('-y', outputPath);

    return args;
}

// Update Job Progress
function updateJobProgress(job, progress, message, steps) {
    job.progress = progress;
    job.message = message;
    job.steps = steps;
}

// Cleanup old jobs (run periodically)
setInterval(() => {
    const now = Date.now();
    for (const [jobId, job] of jobs.entries()) {
        if (now - job.createdAt > 3600000) { // 1 hour
            jobs.delete(jobId);
            console.log(`Cleaned up old job: ${jobId}`);
        }
    }
}, 300000); // Every 5 minutes

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
    console.log(`📁 Upload directory: ${path.join(__dirname, '../uploads')}`);
    console.log(`📹 Output directory: ${path.join(__dirname, '../outputs')}`);
});

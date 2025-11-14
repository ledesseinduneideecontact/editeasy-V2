// Configuration
const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:3000/api'
    : '/api';

// State
let uploadedFiles = [];
let musicFile = null;
let sortable = null;

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const musicInput = document.getElementById('musicInput');
const musicFileName = document.getElementById('musicFileName');
const filesSection = document.getElementById('filesSection');
const filesGrid = document.getElementById('filesGrid');
const fileCount = document.getElementById('fileCount');
const addMoreBtn = document.getElementById('addMoreBtn');
const settingsSection = document.getElementById('settingsSection');
const actionSection = document.getElementById('actionSection');
const generateBtn = document.getElementById('generateBtn');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const progressSteps = document.getElementById('progressSteps');
const resultSection = document.getElementById('resultSection');
const resultVideo = document.getElementById('resultVideo');
const downloadBtn = document.getElementById('downloadBtn');
const newVideoBtn = document.getElementById('newVideoBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeUploadZone();
    initializeMusicUpload();
    initializeButtons();
});

// Upload Zone
function initializeUploadZone() {
    uploadZone.addEventListener('click', () => fileInput.click());

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('drag-over');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('drag-over');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
}

// Music Upload
function initializeMusicUpload() {
    musicInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            musicFile = file;
            musicFileName.textContent = `✓ ${file.name}`;
        }
    });
}

// Buttons
function initializeButtons() {
    addMoreBtn.addEventListener('click', () => fileInput.click());
    generateBtn.addEventListener('click', generateVideo);
    downloadBtn.addEventListener('click', downloadVideo);
    newVideoBtn.addEventListener('click', resetApp);
}

// Handle Files
async function handleFiles(files) {
    const validFiles = Array.from(files).filter(file => {
        const isImage = file.type.startsWith('image/');
        const isVideo = file.type.startsWith('video/');
        return isImage || isVideo;
    });

    if (validFiles.length === 0) {
        alert('Veuillez sélectionner des fichiers images ou vidéos valides.');
        return;
    }

    for (const file of validFiles) {
        const fileData = {
            id: Date.now() + Math.random(),
            file: file,
            name: file.name,
            size: formatFileSize(file.size),
            type: file.type.startsWith('image/') ? 'image' : 'video',
            preview: await createPreview(file)
        };
        uploadedFiles.push(fileData);
    }

    updateFilesDisplay();
}

// Create Preview
function createPreview(file) {
    return new Promise((resolve) => {
        const url = URL.createObjectURL(file);

        if (file.type.startsWith('image/')) {
            const img = new Image();
            img.onload = () => resolve(url);
            img.src = url;
        } else {
            const video = document.createElement('video');
            video.onloadeddata = () => {
                video.currentTime = 1; // Get frame at 1 second
            };
            video.onseeked = () => {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                canvas.getContext('2d').drawImage(video, 0, 0);
                resolve(canvas.toDataURL());
                URL.revokeObjectURL(url);
            };
            video.src = url;
        }
    });
}

// Update Files Display
function updateFilesDisplay() {
    filesGrid.innerHTML = '';
    fileCount.textContent = uploadedFiles.length;

    uploadedFiles.forEach((fileData, index) => {
        const fileItem = createFileItem(fileData, index);
        filesGrid.appendChild(fileItem);
    });

    // Initialize Sortable
    if (sortable) {
        sortable.destroy();
    }
    sortable = Sortable.create(filesGrid, {
        animation: 150,
        ghostClass: 'sortable-ghost',
        onEnd: (evt) => {
            const item = uploadedFiles.splice(evt.oldIndex, 1)[0];
            uploadedFiles.splice(evt.newIndex, 0, item);
            updateFilesDisplay();
        }
    });

    // Show sections
    filesSection.style.display = 'block';
    settingsSection.style.display = 'block';
    actionSection.style.display = 'block';
}

// Create File Item
function createFileItem(fileData, index) {
    const div = document.createElement('div');
    div.className = 'file-item fade-in';
    div.innerHTML = `
        <div class="file-order">${index + 1}</div>
        <button class="file-remove" onclick="removeFile(${fileData.id})">×</button>
        ${fileData.type === 'image'
            ? `<img src="${fileData.preview}" alt="${fileData.name}" class="file-preview">`
            : `<img src="${fileData.preview}" alt="${fileData.name}" class="file-preview">`
        }
        <div class="file-info">
            <div class="file-name-text" title="${fileData.name}">${fileData.name}</div>
            <div class="file-size">${fileData.size}</div>
        </div>
    `;
    return div;
}

// Remove File
window.removeFile = function(fileId) {
    uploadedFiles = uploadedFiles.filter(f => f.id !== fileId);
    if (uploadedFiles.length === 0) {
        filesSection.style.display = 'none';
        settingsSection.style.display = 'none';
        actionSection.style.display = 'none';
    } else {
        updateFilesDisplay();
    }
};

// Generate Video
async function generateVideo() {
    if (uploadedFiles.length === 0) {
        alert('Veuillez ajouter au moins un fichier.');
        return;
    }

    // Hide sections
    filesSection.style.display = 'none';
    settingsSection.style.display = 'none';
    actionSection.style.display = 'none';

    // Show progress
    progressSection.style.display = 'block';

    try {
        // Prepare form data
        const formData = new FormData();

        uploadedFiles.forEach((fileData, index) => {
            formData.append('files', fileData.file);
        });

        if (musicFile) {
            formData.append('music', musicFile);
        }

        // Add settings
        const settings = {
            videoDuration: document.getElementById('videoDuration').value,
            transitionStyle: document.getElementById('transitionStyle').value,
            videoQuality: document.getElementById('videoQuality').value,
            musicSync: document.getElementById('musicSync').value,
            enableStabilization: document.getElementById('enableStabilization').checked,
            enableColorGrading: document.getElementById('enableColorGrading').checked
        };
        formData.append('settings', JSON.stringify(settings));

        // Upload files
        updateProgress(10, 'Upload des fichiers...', [
            { text: 'Upload des fichiers', active: true }
        ]);

        const uploadResponse = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!uploadResponse.ok) {
            throw new Error('Erreur lors de l\'upload');
        }

        const { jobId } = await uploadResponse.json();

        // Poll for progress
        pollProgress(jobId);

    } catch (error) {
        console.error('Error:', error);
        alert('Une erreur est survenue : ' + error.message);
        resetProgress();
    }
}

// Poll Progress
async function pollProgress(jobId) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`${API_URL}/status/${jobId}`);
            const data = await response.json();

            if (data.status === 'completed') {
                clearInterval(interval);
                showResult(data.videoUrl);
            } else if (data.status === 'failed') {
                clearInterval(interval);
                alert('Erreur lors de la génération : ' + data.error);
                resetProgress();
            } else {
                updateProgress(data.progress, data.message, data.steps);
            }
        } catch (error) {
            console.error('Error polling:', error);
        }
    }, 2000);
}

// Update Progress
function updateProgress(percent, message, steps = []) {
    progressFill.style.width = `${percent}%`;
    progressText.textContent = message;

    if (steps.length > 0) {
        progressSteps.innerHTML = steps.map(step => `
            <div class="progress-step ${step.active ? 'active' : ''} ${step.completed ? 'completed' : ''}">
                <span class="progress-step-icon">${step.completed ? '✓' : '⏳'}</span>
                <span>${step.text}</span>
            </div>
        `).join('');
    }
}

// Show Result
function showResult(videoUrl) {
    progressSection.style.display = 'none';
    resultSection.style.display = 'block';
    resultVideo.src = videoUrl;
    window.currentVideoUrl = videoUrl;
}

// Download Video
function downloadVideo() {
    const a = document.createElement('a');
    a.href = window.currentVideoUrl;
    a.download = `video-${Date.now()}.mp4`;
    a.click();
}

// Reset App
function resetApp() {
    uploadedFiles = [];
    musicFile = null;
    musicFileName.textContent = '';
    fileInput.value = '';
    musicInput.value = '';

    resultSection.style.display = 'none';
    filesSection.style.display = 'none';
    settingsSection.style.display = 'none';
    actionSection.style.display = 'none';

    document.getElementById('uploadSection').style.display = 'block';
}

// Reset Progress
function resetProgress() {
    progressSection.style.display = 'none';
    filesSection.style.display = 'block';
    settingsSection.style.display = 'block';
    actionSection.style.display = 'block';
}

// Utilities
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

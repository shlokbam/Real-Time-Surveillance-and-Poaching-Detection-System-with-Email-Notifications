// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const videoInput = document.getElementById('videoInput');
const uploadText = document.getElementById('uploadText');
const uploadBtn = document.getElementById('uploadBtn');
const startCameraBtn = document.getElementById('startCameraBtn');
const stopBtn = document.getElementById('stopBtn');
const videoFeed = document.getElementById('videoFeed');
const placeholder = document.getElementById('placeholder');
const statusBadge = document.getElementById('statusBadge');
const statusText = document.getElementById('statusText');
const downloadBtn = document.getElementById('downloadBtn');
const galleryBtn = document.getElementById('galleryBtn');
const notificationArea = document.getElementById('notificationArea');
const totalDetections = document.getElementById('totalDetections');
const emailsSent = document.getElementById('emailsSent');
const lastDetection = document.getElementById('lastDetection');
const fpsBadge = document.getElementById('fpsBadge');
const galleryModal = document.getElementById('galleryModal');
const closeGalleryBtn = document.getElementById('closeGalleryBtn');
const galleryGrid = document.getElementById('galleryGrid');
const imageModal = document.getElementById('imageModal');
const modalClose = document.getElementById('modalClose');
const modalImage = document.getElementById('modalImage');
const modalTimestamp = document.getElementById('modalTimestamp');
const deleteImageBtn = document.getElementById('deleteImageBtn');
const toastContainer = document.getElementById('toastContainer');

let selectedFile = null;
let statsInterval = null;
let currentImageFilename = null;
let lastDetectionCount = 0;

// Upload Area Interactions
uploadArea.addEventListener('click', () => videoInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

videoInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/webm', 'video/x-matroska'];
    
    if (validTypes.includes(file.type)) {
        selectedFile = file;
        uploadArea.classList.add('has-file');
        uploadText.textContent = `✓ ${file.name}`;
        uploadBtn.disabled = false;
        showToast('File selected successfully', 'success');
    } else {
        showToast('Invalid file type. Please select a video file.', 'error');
    }
}

// Upload Video
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('video', selectedFile);
    
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span>⏳</span> Processing...';
    
    try {
        const response = await fetch('/upload_video', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message, 'success');
            startVideoFeed();
            setDetectionState(true);
        } else {
            showToast(data.message, 'error');
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<span>🚀</span> Start Detection';
        }
    } catch (error) {
        showToast('Error uploading video', 'error');
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = '<span>🚀</span> Start Detection';
    }
});

// Start Camera
startCameraBtn.addEventListener('click', async () => {
    startCameraBtn.disabled = true;
    startCameraBtn.innerHTML = '<span>⏳</span> Starting...';
    
    try {
        const response = await fetch('/start_camera', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message, 'success');
            startVideoFeed();
            setDetectionState(true);
        } else {
            showToast(data.message, 'error');
            startCameraBtn.disabled = false;
            startCameraBtn.innerHTML = '<span>📹</span> Start Live Camera';
        }
    } catch (error) {
        showToast('Error starting camera', 'error');
        startCameraBtn.disabled = false;
        startCameraBtn.innerHTML = '<span>📹</span> Start Live Camera';
    }
});

// Stop Detection
stopBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/stop_detection', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message, 'success');
            stopVideoFeed();
            setDetectionState(false);
        }
    } catch (error) {
        showToast('Error stopping detection', 'error');
    }
});

// Download Excel
downloadBtn.addEventListener('click', () => {
    window.location.href = '/download_excel';
    showToast('Downloading detection log...', 'info');
});

// Gallery
galleryBtn.addEventListener('click', () => {
    galleryModal.classList.add('show');
    loadGallery();
});

closeGalleryBtn.addEventListener('click', () => {
    galleryModal.classList.remove('show');
});

async function loadGallery() {
    try {
        const response = await fetch('/get_detected_images');
        const data = await response.json();
        
        if (data.success) {
            displayGallery(data.images);
        } else {
            showToast('Error loading images', 'error');
        }
    } catch (error) {
        showToast('Error loading gallery', 'error');
    }
}

function displayGallery(images) {
    if (images.length === 0) {
        galleryGrid.innerHTML = '<div class="gallery-placeholder"><p>No images detected yet</p></div>';
        return;
    }
    
    galleryGrid.innerHTML = '';
    
    images.forEach(image => {
        const item = document.createElement('div');
        item.className = 'gallery-item';
        item.innerHTML = `
            <img src="${image.url}" alt="Detection" loading="lazy">
            <div class="gallery-item-info">
                <div class="gallery-item-time">
                    <span>🕐</span>
                    <span>${image.timestamp}</span>
                </div>
            </div>
        `;
        
        item.addEventListener('click', () => {
            openImageModal(image.url, image.timestamp, image.filename);
        });
        
        galleryGrid.appendChild(item);
    });
}

function openImageModal(imageUrl, timestamp, filename) {
    currentImageFilename = filename;
    modalImage.src = imageUrl;
    modalTimestamp.textContent = `Detected at: ${timestamp}`;
    imageModal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeImageModal() {
    imageModal.classList.remove('show');
    document.body.style.overflow = 'auto';
    currentImageFilename = null;
}

modalClose.addEventListener('click', closeImageModal);

imageModal.addEventListener('click', (e) => {
    if (e.target === imageModal) closeImageModal();
});

galleryModal.addEventListener('click', (e) => {
    if (e.target === galleryModal) galleryModal.classList.remove('show');
});

deleteImageBtn.addEventListener('click', async () => {
    if (!currentImageFilename) return;
    
    if (confirm('Are you sure you want to delete this image?')) {
        try {
            const response = await fetch(`/delete_image/${currentImageFilename}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                showToast('Image deleted successfully', 'success');
                closeImageModal();
                loadGallery();
            } else {
                showToast('Error deleting image', 'error');
            }
        } catch (error) {
            showToast('Error deleting image', 'error');
        }
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeImageModal();
        galleryModal.classList.remove('show');
    }
});

// Video Feed Management
function startVideoFeed() {
    placeholder.style.display = 'none';
    videoFeed.src = '/video_feed?' + new Date().getTime();
    videoFeed.style.display = 'block';
    
    videoFeed.onerror = () => {
        setTimeout(() => {
            if (videoFeed.style.display === 'block') {
                videoFeed.src = '/video_feed?' + new Date().getTime();
            }
        }, 1000);
    };
    
    startStatsPolling();
}

function stopVideoFeed() {
    videoFeed.src = '';
    videoFeed.style.display = 'none';
    placeholder.style.display = 'block';
    stopStatsPolling();
}

function setDetectionState(active) {
    if (active) {
        statusBadge.classList.add('active');
        statusText.textContent = 'Active';
        uploadBtn.disabled = true;
        startCameraBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        statusBadge.classList.remove('active');
        statusText.textContent = 'Standby';
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = '<span>🚀</span> Start Detection';
        startCameraBtn.disabled = false;
        startCameraBtn.innerHTML = '<span>📹</span> Start Live Camera';
        stopBtn.disabled = true;
        
        uploadArea.classList.remove('has-file');
        uploadText.textContent = 'Click or drag video here';
        selectedFile = null;
        videoInput.value = '';
    }
}

// Stats Polling
function startStatsPolling() {
    updateStats();
    statsInterval = setInterval(updateStats, 2000);
}

function stopStatsPolling() {
    if (statsInterval) {
        clearInterval(statsInterval);
        statsInterval = null;
    }
}

async function updateStats() {
    try {
        const response = await fetch('/get_stats');
        const stats = await response.json();
        
        totalDetections.textContent = stats.total_detections || 0;
        emailsSent.textContent = stats.emails_sent || 0;
        fpsBadge.textContent = `${stats.current_fps || 0} FPS`;
        
        if (stats.last_detection_time) {
            lastDetection.textContent = stats.last_detection_time;
            
            if (lastDetectionCount < stats.total_detections) {
                addNotification(stats.last_detection_time);
                
                if (galleryModal.classList.contains('show')) {
                    loadGallery();
                }
            }
            lastDetectionCount = stats.total_detections;
        } else {
            lastDetection.textContent = 'Never';
        }
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// Notifications
function addNotification(timestamp) {
    const notification = document.createElement('div');
    notification.className = 'notification-item';
    notification.innerHTML = `
        <div class="notification-header">
            <span>📧</span>
            <span>Alert Sent</span>
        </div>
        <div class="notification-body">
            Poaching detected at ${timestamp}<br>
            Email alert sent successfully
        </div>
    `;
    
    if (notificationArea.querySelector('.no-notifications')) {
        notificationArea.innerHTML = '';
    }
    
    notificationArea.insertBefore(notification, notificationArea.firstChild);
    
    while (notificationArea.children.length > 5) {
        notificationArea.removeChild(notificationArea.lastChild);
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('WildGuard AI Dashboard Initialized');
    updateStats();
});
// DOM Elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const preview = document.getElementById('preview');
const statusDiv = document.getElementById('status');
const downloadLink = document.getElementById('downloadLink');

// Global variables
let recorder = null;
let mediaStreams = [];

// Update status message
function updateStatus(message, type = '') {
    statusDiv.textContent = message;
    statusDiv.className = type;
}

// Clean up all resources
async function cleanup() {
    try {
        // Stop all media tracks
        mediaStreams.forEach(stream => {
            stream.getTracks().forEach(track => {
                track.stop();
                track.enabled = false;
            });
        });
        mediaStreams = [];

        // Reset preview
        if (preview.srcObject) {
            preview.srcObject.getTracks().forEach(track => track.stop());
            preview.srcObject = null;
        }
        preview.style.display = 'none';

        // Destroy recorder
        if (recorder) {
            try {
                if (recorder.state === 'recording') {
                    recorder.stopRecording();
                }
                recorder.destroy();
                recorder = null;
            } catch (e) {
                console.warn('Recorder cleanup error:', e);
            }
        }
    } catch (error) {
        console.error('Cleanup error:', error);
    } finally {
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

// Start recording
startBtn.addEventListener('click', async () => {
    try {
        updateStatus('Requesting permissions...');
        startBtn.disabled = true;
        stopBtn.disabled = true;

        // 1. Get screen stream with system audio
        const screenStream = await navigator.mediaDevices.getDisplayMedia({
            video: {
                displaySurface: 'browser',
                frameRate: 30
            },
            audio: true
        }).catch(err => {
            throw new Error(`Screen sharing error: ${err.message}`);
        });

        if (!screenStream) {
            throw new Error('Screen sharing was cancelled');
        }

        // 2. Get microphone
        const micStream = await navigator.mediaDevices.getUserMedia({
            audio: true,
            video: false
        }).catch(err => {
            screenStream.getTracks().forEach(track => track.stop());
            throw new Error(`Microphone error: ${err.message}`);
        });

        // Store streams for cleanup
        mediaStreams = [screenStream, micStream];

        // 3. Combine streams
        const combinedStream = new MediaStream([
            ...screenStream.getVideoTracks(),
            ...screenStream.getAudioTracks(),
            ...micStream.getAudioTracks()
        ]);

        // Show preview
        preview.srcObject = combinedStream;
        preview.style.display = 'block';
        preview.muted = true;

        // 4. Setup recorder with error handling
        recorder = new RecordRTC(combinedStream, {
            type: 'video',
            mimeType: 'video/webm',
            bitsPerSecond: 8000000,
            disableLogs: false,
            ondataavailable: function(blob) {
                console.log('Recording data available:', blob.size);
            },
            onerror: function(error) {
                console.error('Recorder error:', error);
                updateStatus(`Recorder error: ${error}`, 'error');
            }
        });

        // Start recording
        recorder.startRecording();
        updateStatus('Recording...', 'recording');
        stopBtn.disabled = false;

    } catch (error) {
        console.error('Recording start failed:', error);
        updateStatus(`Error: ${error.message}`, 'error');
        await cleanup();
    }
});

// Stop recording and process
stopBtn.addEventListener('click', async () => {
    if (!recorder) return;

    try {
        updateStatus('Stopping recording...');
        stopBtn.disabled = true;

        // 1. Stop recording with timeout
        const stopPromise = new Promise((resolve) => {
            recorder.stopRecording(() => {
                console.log('Recording successfully stopped');
                resolve();
            });
        });

        const timeoutPromise = new Promise(resolve => {
            setTimeout(() => {
                console.warn('Forced recording stop after timeout');
                resolve();
            }, 3000); // 3 seconds timeout
        });

        await Promise.race([stopPromise, timeoutPromise]);

        // 2. Get recording blob
        const blob = recorder.getBlob();
        if (!blob || blob.size === 0) {
            throw new Error('Recorded video is empty or corrupted');
        }

        // 3. Prepare for upload
        updateStatus('Preparing upload...');
        const formData = new FormData();
        formData.append('video', blob, `recording_${Date.now()}.webm`);

        // 4. Send to server with timeout
        updateStatus('Uploading to server...');
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000); // 15s timeout

        const response = await fetch('/process_video/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Accept': 'application/json'
            },
            signal: controller.signal
        }).finally(() => clearTimeout(timeoutId));

        // 5. Handle response
        if (!response.ok) {
            const error = await response.json().catch(() => null);
            throw new Error(error?.error || `Server error: ${response.status}`);
        }

        const result = await response.json();
        displayResults(result);
        updateStatus('Processing completed!', 'success');

    } catch (error) {
        console.error('Stop recording error:', error);
        updateStatus(`Error: ${error.message}`, 'error');
    } finally {
        await cleanup();
    }
});

// Helper functions
function getCSRFToken() {
    const cookie = document.cookie.match(/csrftoken=([^;]+)/);
    return cookie ? cookie[1] : '';
}

function displayResults(result) {
    if (!result?.transcription) {
        downloadLink.innerHTML = '<div class="error">No transcription data received</div>';
        return;
    }

    let html = '<h3>Transcript:</h3><ul>';
    result.transcription.forEach(item => {
        html += `
            <li>
                <strong>${item.name || 'Unknown'}</strong>
                (${item.start?.toFixed(1) || '0.0'}s-${item.end?.toFixed(1) || '0.0'}s):
                ${item.text || 'No text'}
            </li>
        `;
    });
    html += '</ul>';
    downloadLink.innerHTML = html;
}

// Handle page exit
window.addEventListener('beforeunload', (e) => {
    if (recorder?.state === 'recording') {
        e.preventDefault();
        return e.returnValue = 'You have an active recording. Are you sure you want to leave?';
    }
});
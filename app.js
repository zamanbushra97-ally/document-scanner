// Document Scanner Frontend - Vercel Compatible Version

// Detect if running on Vercel or localhost
const API_BASE = window.location.hostname === 'localhost'
    ? 'http://localhost:5000/api'
    : '/api';  // Vercel serverless functions

// State
let uploadedFiles = [];
let processingResults = [];

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const clearBtn = document.getElementById('clearBtn');
const processBtn = document.getElementById('processBtn');
const statusSection = document.getElementById('statusSection');
const statusText = document.getElementById('statusText');
const progressFill = document.getElementById('progressFill');
const resultsSection = document.getElementById('resultsSection');
const resultsGrid = document.getElementById('resultsGrid');
const exportJsonBtn = document.getElementById('exportJsonBtn');
const exportCsvBtn = document.getElementById('exportCsvBtn');
const resultModal = document.getElementById('resultModal');
const modalClose = document.getElementById('modalClose');
const modalTitle = document.getElementById('modalTitle');
const modalBody = document.getElementById('modalBody');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkServerHealth();
});

function setupEventListeners() {
    // Drop zone events
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);

    // File input
    fileInput.addEventListener('change', handleFileSelect);

    // Buttons
    clearBtn.addEventListener('click', clearFiles);
    processBtn.addEventListener('click', processDocuments);
    exportJsonBtn.addEventListener('click', exportJSON);
    exportCsvBtn.addEventListener('click', exportCSV);

    // Modal
    modalClose.addEventListener('click', closeModal);
    resultModal.addEventListener('click', (e) => {
        if (e.target === resultModal) closeModal();
    });
}

async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        console.log('Server status:', data);
    } catch (error) {
        console.warn('Server health check failed:', error);
    }
}

// Drag and Drop Handlers
function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
}

// File Management
function addFiles(files) {
    files.forEach(file => {
        if (!uploadedFiles.find(f => f.name === file.name)) {
            uploadedFiles.push(file);
        }
    });

    renderFileList();
    updateButtons();
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    renderFileList();
    updateButtons();
}

function clearFiles() {
    uploadedFiles = [];
    renderFileList();
    updateButtons();
}

function renderFileList() {
    if (uploadedFiles.length === 0) {
        fileList.innerHTML = '';
        return;
    }

    fileList.innerHTML = uploadedFiles.map((file, index) => `
        <div class="file-item">
            <div class="file-info">
                <div class="file-icon">${file.name.split('.').pop().toUpperCase()}</div>
                <div class="file-details">
                    <h4>${file.name}</h4>
                    <span class="file-size">${formatFileSize(file.size)}</span>
                </div>
            </div>
            <button class="file-remove" onclick="removeFile(${index})">&times;</button>
        </div>
    `).join('');
}

function updateButtons() {
    const hasFiles = uploadedFiles.length > 0;
    clearBtn.disabled = !hasFiles;
    processBtn.disabled = !hasFiles;
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Convert file to base64 for serverless processing
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// Document Processing
async function processDocuments() {
    if (uploadedFiles.length === 0) return;

    // Show status section
    statusSection.style.display = 'block';
    resultsSection.style.display = 'none';
    processBtn.disabled = true;

    try {
        // Convert files to base64
        updateStatus('Preparing files...', 10);
        const filesData = await Promise.all(
            uploadedFiles.map(async (file) => ({
                filename: file.name,
                data: await fileToBase64(file),
                size: file.size
            }))
        );

        // Process with OCR
        updateStatus('Processing with OCR...', 30);
        const response = await fetch(`${API_BASE}/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                files: filesData
            })
        });

        if (!response.ok) {
            throw new Error('Processing failed');
        }

        const data = await response.json();

        // Display results
        updateStatus('Rendering results...', 90);
        processingResults = data.results;
        renderResults(data.results);

        updateStatus('Complete!', 100);

        // Hide status, show results
        setTimeout(() => {
            statusSection.style.display = 'none';
            resultsSection.style.display = 'block';
        }, 1000);

    } catch (error) {
        console.error('Processing error:', error);
        updateStatus(`Error: ${error.message}`, 0);
        alert('Processing failed: ' + error.message);
    } finally {
        processBtn.disabled = false;
    }
}

function updateStatus(text, progress) {
    statusText.textContent = text;
    progressFill.style.width = `${progress}%`;
}

// Results Display
function renderResults(results) {
    resultsGrid.innerHTML = results.map((result, index) => {
        const docType = result.document_type || 'unknown';
        const badgeClass = `badge-${docType}`;
        const confidence = (result.ocr?.confidence * 100 || 0).toFixed(1);
        const wordCount = result.ocr?.word_count || 0;
        const text = result.ocr?.text || '';
        const preview = text.substring(0, 200) + (text.length > 200 ? '...' : '');

        return `
            <div class="result-card" onclick="showResultDetail(${index})">
                <div class="result-header">
                    <div>
                        <div class="result-title">${result.file_name}</div>
                    </div>
                    <span class="result-badge ${badgeClass}">${docType}</span>
                </div>
                <div class="result-text">${preview || 'No text extracted'}</div>
                <div class="result-meta">
                    <div class="meta-item">
                        <span class="meta-label">Confidence</span>
                        <span class="meta-value">${confidence}%</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Words</span>
                        <span class="meta-value">${wordCount}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Engine</span>
                        <span class="meta-value">${result.ocr?.engine || 'Tesseract'}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function showResultDetail(index) {
    const result = processingResults[index];

    modalTitle.textContent = result.file_name;

    const metadata = result.metadata || {};

    modalBody.innerHTML = `
        <div style="margin-bottom: 2rem;">
            <h4 style="margin-bottom: 1rem; color: var(--primary);">Extracted Text</h4>
            <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px; max-height: 300px; overflow-y: auto; line-height: 1.8;">
                ${result.ocr?.text || 'No text extracted'}
            </div>
        </div>
        
        <div style="margin-bottom: 2rem;">
            <h4 style="margin-bottom: 1rem; color: var(--primary);">Metadata</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                ${metadata.dates?.length ? `
                    <div>
                        <strong>Dates:</strong><br>
                        ${metadata.dates.join(', ')}
                    </div>
                ` : ''}
                ${metadata.emails?.length ? `
                    <div>
                        <strong>Emails:</strong><br>
                        ${metadata.emails.join(', ')}
                    </div>
                ` : ''}
                ${metadata.phone_numbers?.length ? `
                    <div>
                        <strong>Phone Numbers:</strong><br>
                        ${metadata.phone_numbers.join(', ')}
                    </div>
                ` : ''}
                ${metadata.amounts?.length ? `
                    <div>
                        <strong>Amounts:</strong><br>
                        ${metadata.amounts.join(', ')}
                    </div>
                ` : ''}
            </div>
        </div>
    `;

    resultModal.classList.add('active');
}

function closeModal() {
    resultModal.classList.remove('active');
}

// Export Functions
async function exportJSON() {
    const dataStr = JSON.stringify(processingResults, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    downloadBlob(blob, 'scan_results.json');
}

async function exportCSV() {
    // Generate CSV from results
    const headers = ['Filename', 'Confidence', 'Word Count', 'Dates', 'Emails', 'Phone Numbers'];
    const rows = processingResults.map(r => [
        r.file_name,
        (r.ocr?.confidence * 100 || 0).toFixed(1) + '%',
        r.ocr?.word_count || 0,
        r.metadata?.dates?.join('; ') || '',
        r.metadata?.emails?.join('; ') || '',
        r.metadata?.phone_numbers?.join('; ') || ''
    ]);

    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    downloadBlob(blob, 'scan_results.csv');
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Make functions globally accessible
window.removeFile = removeFile;
window.showResultDetail = showResultDetail;

<template>
  <div class="page-container">
    <div class="page-header animate-fade-in-up">
      <h1 class="page-title">Upload Resume</h1>
      <p class="page-subtitle">Drag & drop or select a PDF/DOCX file for AI-powered analysis.</p>
    </div>

    <div v-if="error" class="alert alert-error animate-fade-in">{{ error }}</div>
    <div v-if="success" class="alert alert-success animate-fade-in">{{ success }}</div>

    <!-- Upload zone -->
    <div
      class="upload-zone glass-card animate-fade-in-up"
      :class="{ 'drag-over': isDragging, 'uploading': uploading }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
      id="upload-zone"
      style="animation-delay: 100ms"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf,.docx"
        @change="handleFileSelect"
        hidden
      />

      <div v-if="uploading" class="upload-progress">
        <div class="spinner"></div>
        <h3>Analyzing Your Resume...</h3>
        <p>Our AI is extracting skills, scoring your resume, and finding matching jobs.</p>
        <div class="progress-bar" style="max-width: 300px; margin: 1rem auto">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <span class="progress-text">{{ progressText }}</span>
      </div>

      <div v-else-if="selectedFile" class="file-preview">
        <div class="file-icon">{{ selectedFile.name.endsWith('.pdf') ? '📕' : '📘' }}</div>
        <h3>{{ selectedFile.name }}</h3>
        <p class="file-size">{{ formatSize(selectedFile.size) }}</p>
        <div class="file-actions">
          <button class="btn btn-primary" @click.stop="uploadFile" id="btn-upload-confirm">
            🚀 Analyze Resume
          </button>
          <button class="btn btn-secondary" @click.stop="clearFile">✕ Remove</button>
        </div>
      </div>

      <div v-else class="upload-placeholder">
        <div class="upload-icon">📄</div>
        <h3>Drop your resume here</h3>
        <p>or click to browse files</p>
        <div class="upload-formats">
          <span class="badge badge-primary">PDF</span>
          <span class="badge badge-primary">DOCX</span>
          <span class="upload-max">Max 10MB</span>
        </div>
      </div>
    </div>

    <!-- Tips -->
    <div class="tips-section animate-fade-in-up" style="animation-delay: 200ms">
      <h3 class="section-title">💡 Tips for Best Results</h3>
      <div class="tips-grid">
        <div class="tip-card glass-card">
          <span class="tip-icon">📝</span>
          <h4>Use Standard Formats</h4>
          <p>Stick to clean PDF or DOCX files. Avoid scanned images or heavily designed templates.</p>
        </div>
        <div class="tip-card glass-card">
          <span class="tip-icon">🏷️</span>
          <h4>Label Your Sections</h4>
          <p>Use clear headings like "Experience", "Skills", "Education" for accurate parsing.</p>
        </div>
        <div class="tip-card glass-card">
          <span class="tip-icon">📊</span>
          <h4>Include Keywords</h4>
          <p>Add relevant technical skills and tools. Our AI matches these against job descriptions.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../composables/useApi'

const router = useRouter()

const fileInput = ref(null)
const selectedFile = ref(null)
const isDragging = ref(false)
const uploading = ref(false)
const progress = ref(0)
const progressText = ref('')
const error = ref('')
const success = ref('')

function triggerFileInput() {
  if (!uploading.value && !selectedFile.value) {
    fileInput.value.click()
  }
}

function handleFileSelect(e) {
  const file = e.target.files[0]
  if (file) validateAndSet(file)
}

function handleDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) validateAndSet(file)
}

function validateAndSet(file) {
  error.value = ''
  const ext = file.name.split('.').pop().toLowerCase()
  if (!['pdf', 'docx'].includes(ext)) {
    error.value = 'Only PDF and DOCX files are supported.'
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    error.value = 'File size must be under 10MB.'
    return
  }
  selectedFile.value = file
}

function clearFile() {
  selectedFile.value = null
  fileInput.value.value = ''
}

async function uploadFile() {
  if (!selectedFile.value) return
  error.value = ''
  success.value = ''
  uploading.value = true
  progress.value = 10
  progressText.value = 'Uploading file...'

  try {
    const formData = new FormData()
    formData.append('resume', selectedFile.value)

    progress.value = 30
    progressText.value = 'Processing with AI...'

    const res = await api.post('/api/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    progress.value = 100
    progressText.value = 'Complete!'
    success.value = 'Resume uploaded! Analysis is in progress.'

    // Wait then redirect
    setTimeout(() => {
      router.push(`/analysis/${res.data.resume.id}`)
    }, 1500)
  } catch (err) {
    error.value = err.response?.data?.error || 'Upload failed. Please try again.'
    uploading.value = false
  }
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}
</script>

<style scoped>
.upload-zone {
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  border: 2px dashed var(--border-light);
  border-radius: var(--radius-xl);
  transition: all var(--transition-base);
  margin-bottom: 2.5rem;
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-zone:hover {
  border-color: var(--accent-primary);
  background: var(--accent-primary-glow);
}

.upload-zone.drag-over {
  border-color: var(--accent-primary-light);
  background: rgba(99, 102, 241, 0.1);
  transform: scale(1.01);
}

.upload-zone.uploading {
  cursor: default;
  border-style: solid;
  border-color: var(--accent-primary);
}

.upload-placeholder .upload-icon {
  font-size: 56px;
  margin-bottom: 1rem;
  opacity: 0.7;
}

.upload-placeholder h3 {
  font-size: var(--font-size-xl);
  margin-bottom: 0.25rem;
}

.upload-placeholder p {
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.upload-formats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.upload-max {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

/* File preview */
.file-preview .file-icon {
  font-size: 48px;
  margin-bottom: 0.75rem;
}

.file-preview h3 {
  font-size: var(--font-size-lg);
  margin-bottom: 0.25rem;
}

.file-size {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
  margin-bottom: 1rem;
}

.file-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

/* Progress */
.upload-progress h3 {
  margin-top: 1rem;
  font-size: var(--font-size-lg);
}

.upload-progress p {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.progress-text {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

/* Tips */
.tips-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.tip-card {
  padding: 1.5rem;
  text-align: center;
}

.tip-icon {
  font-size: 28px;
  display: block;
  margin-bottom: 0.75rem;
}

.tip-card h4 {
  font-size: var(--font-size-sm);
  margin-bottom: 0.5rem;
}

.tip-card p {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  line-height: 1.5;
}

@media (max-width: 768px) {
  .tips-grid {
    grid-template-columns: 1fr;
  }
}
</style>

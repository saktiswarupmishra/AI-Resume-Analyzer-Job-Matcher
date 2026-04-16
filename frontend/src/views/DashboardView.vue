<template>
  <div class="page-container">
    <div class="page-header animate-fade-in-up">
      <h1 class="page-title">Dashboard</h1>
      <p class="page-subtitle">Welcome back, {{ user?.name }}! Manage your resumes and track your progress.</p>
    </div>

    <!-- Stats row -->
    <div class="stats-grid animate-fade-in-up" style="animation-delay: 100ms">
      <div class="stat-card glass-card">
        <div class="stat-icon" style="background: var(--accent-primary-glow); color: var(--accent-primary-light)">📄</div>
        <div class="stat-info">
          <div class="stat-value">{{ resumes.length }}</div>
          <div class="stat-label">Resumes Uploaded</div>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-icon" style="background: var(--success-bg); color: var(--success)">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgScore }}</div>
          <div class="stat-label">Avg ATS Score</div>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-icon" style="background: var(--info-bg); color: var(--info)">🎯</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalJobs }}</div>
          <div class="stat-label">Jobs Matched</div>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-icon" style="background: var(--warning-bg); color: var(--warning)">⚡</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalSkills }}</div>
          <div class="stat-label">Skills Detected</div>
        </div>
      </div>
    </div>

    <!-- Quick action -->
    <div class="quick-action animate-fade-in-up" style="animation-delay: 200ms">
      <router-link to="/upload" class="btn btn-primary btn-lg" id="btn-upload-new">
        📄 Upload New Resume
      </router-link>
    </div>

    <!-- Resume history -->
    <div class="resume-section animate-fade-in-up" style="animation-delay: 300ms">
      <h2 class="section-title">Recent Resumes</h2>

      <div v-if="loading" class="empty-state">
        <div class="spinner"></div>
        <p style="margin-top: 1rem">Loading your resumes...</p>
      </div>

      <div v-else-if="resumes.length === 0" class="empty-state glass-card">
        <div class="empty-state-icon">📄</div>
        <h3>No Resumes Yet</h3>
        <p>Upload your first resume to get AI-powered analysis and job recommendations.</p>
        <router-link to="/upload" class="btn btn-primary">Upload Resume</router-link>
      </div>

      <div v-else class="resume-list stagger">
        <div v-for="resume in resumes" :key="resume.id" class="resume-card glass-card animate-fade-in-up">
          <div class="resume-card-header">
            <div class="resume-file-icon">{{ resume.fileType === 'pdf' ? '📕' : '📘' }}</div>
            <div class="resume-info">
              <h3 class="resume-name">{{ resume.fileName }}</h3>
              <span class="resume-date">{{ formatDate(resume.createdAt) }}</span>
            </div>
            <div class="resume-score-mini">
              <span class="badge" :class="getScoreBadge(resume.analysisResult?.atsScore)">
                {{ resume.analysisResult?.atsScore ?? '—' }}/100
              </span>
            </div>
          </div>

          <div class="resume-stats-row">
            <span class="resume-stat">
              <span class="stat-dot" style="background: var(--accent-primary)"></span>
              {{ resume._count?.skills || 0 }} Skills
            </span>
            <span class="resume-stat">
              <span class="stat-dot" style="background: var(--success)"></span>
              {{ resume._count?.jobMatches || 0 }} Jobs Matched
            </span>
            <span class="badge" :class="getStatusBadge(resume.status)">{{ resume.status }}</span>
          </div>

          <div class="resume-actions">
            <router-link :to="`/analysis/${resume.id}`" class="btn btn-secondary btn-sm" v-if="resume.status === 'analyzed'">
              📊 View Analysis
            </router-link>
            <router-link :to="`/jobs/${resume.id}`" class="btn btn-secondary btn-sm" v-if="resume.status === 'analyzed'">
              🎯 View Jobs
            </router-link>
            <button class="btn btn-danger btn-sm" @click="deleteResume(resume.id)">🗑️</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'
import api from '../composables/useApi'

const { user } = useAuth()

const resumes = ref([])
const loading = ref(true)

const avgScore = computed(() => {
  const scored = resumes.value.filter(r => r.analysisResult?.atsScore)
  if (scored.length === 0) return 0
  return Math.round(scored.reduce((sum, r) => sum + r.analysisResult.atsScore, 0) / scored.length)
})

const totalJobs = computed(() => resumes.value.reduce((sum, r) => sum + (r._count?.jobMatches || 0), 0))
const totalSkills = computed(() => resumes.value.reduce((sum, r) => sum + (r._count?.skills || 0), 0))

async function fetchResumes() {
  loading.value = true
  try {
    const res = await api.get('/api/resume/list')
    resumes.value = res.data.resumes
  } catch (err) {
    console.error('Failed to fetch resumes:', err)
  } finally {
    loading.value = false
  }
}

async function deleteResume(id) {
  if (!confirm('Delete this resume?')) return
  try {
    await api.delete(`/api/resume/${id}`)
    resumes.value = resumes.value.filter(r => r.id !== id)
  } catch (err) {
    alert('Delete failed.')
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

function getScoreBadge(score) {
  if (!score) return 'badge-info'
  if (score >= 80) return 'badge-success'
  if (score >= 50) return 'badge-warning'
  return 'badge-danger'
}

function getStatusBadge(status) {
  const map = { analyzed: 'badge-success', parsing: 'badge-warning', uploaded: 'badge-info', failed: 'badge-danger' }
  return map[status] || 'badge-info'
}

onMounted(fetchResumes)
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: 800;
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.quick-action {
  margin-bottom: 2rem;
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: 700;
  margin-bottom: 1.25rem;
}

.resume-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.resume-card {
  padding: 1.25rem 1.5rem;
}

.resume-card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.resume-file-icon {
  font-size: 28px;
}

.resume-info {
  flex: 1;
}

.resume-name {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: 0.15rem;
}

.resume-date {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.resume-stats-row {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 0.75rem;
}

.resume-stat {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.stat-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.resume-actions {
  display: flex;
  gap: 0.5rem;
}

@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 500px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<template>
  <div class="page-container">
    <!-- Loading state -->
    <div v-if="loading" class="empty-state">
      <div class="spinner"></div>
      <p style="margin-top: 1rem">Loading analysis...</p>
    </div>

    <!-- Polling state -->
    <div v-else-if="resume && resume.status !== 'analyzed'" class="empty-state glass-card animate-fade-in-up">
      <div class="spinner" style="margin: 0 auto"></div>
      <h3 style="margin-top: 1.5rem">Analysis In Progress</h3>
      <p>Our AI is analyzing your resume. This usually takes 15-30 seconds.</p>
      <p class="text-muted" style="font-size: var(--font-size-xs); margin-top: 0.5rem">
        Status: <span class="badge badge-warning">{{ resume.status }}</span>
      </p>
    </div>

    <!-- Analysis results -->
    <div v-else-if="resume && resume.analysisResult" class="analysis-content">
      <div class="page-header animate-fade-in-up">
        <div class="header-row">
          <div>
            <h1 class="page-title">Analysis Report</h1>
            <p class="page-subtitle">{{ resume.fileName }} — {{ formatDate(resume.createdAt) }}</p>
          </div>
          <div class="header-actions">
            <router-link :to="`/jobs/${resume.id}`" class="btn btn-primary">
              🎯 View Jobs ({{ resume.jobMatches?.length || 0 }})
            </router-link>
            <router-link to="/dashboard" class="btn btn-secondary">← Dashboard</router-link>
          </div>
        </div>
      </div>

      <!-- Score + Summary row -->
      <div class="score-summary-grid animate-fade-in-up" style="animation-delay: 100ms">
        <!-- ATS Score -->
        <div class="glass-card score-card">
          <div class="score-ring">
            <svg width="140" height="140" viewBox="0 0 140 140">
              <circle class="ring-bg" cx="70" cy="70" r="60" />
              <circle
                class="ring-fill"
                cx="70" cy="70" r="60"
                :stroke="scoreColor"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="scoreOffset"
              />
            </svg>
            <div class="score-text">
              <div class="score-value" :style="{ color: scoreColor }">
                {{ resume.analysisResult.atsScore }}
              </div>
              <div class="score-label">ATS Score</div>
            </div>
          </div>
          <div class="score-message">
            <span :class="scoreLevel.class">{{ scoreLevel.label }}</span>
          </div>
        </div>

        <!-- Summary -->
        <div class="glass-card summary-card">
          <h3>📝 Summary</h3>
          <p>{{ resume.analysisResult.summary || 'No summary available.' }}</p>
          <div class="summary-meta">
            <div v-if="resume.analysisResult.experienceYears">
              <span class="meta-label">Experience</span>
              <span class="meta-value">~{{ resume.analysisResult.experienceYears }} years</span>
            </div>
            <div v-if="resume.analysisResult.educationLevel">
              <span class="meta-label">Education</span>
              <span class="meta-value">{{ formatEducation(resume.analysisResult.educationLevel) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Score breakdown -->
      <div class="glass-card animate-fade-in-up" style="animation-delay: 200ms">
        <h3 style="margin-bottom: 1.25rem">📊 Score Breakdown</h3>
        <div class="breakdown-list">
          <div v-for="(item, key) in resume.analysisResult.scoreBreakdown" :key="key" class="breakdown-item">
            <div class="breakdown-header">
              <span class="breakdown-name">{{ formatBreakdownName(key) }}</span>
              <span class="breakdown-score">{{ item.score }} / {{ item.max }}</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: (item.score / item.max * 100) + '%' }"></div>
            </div>
            <p class="breakdown-detail">{{ item.detail }}</p>
          </div>
        </div>
      </div>

      <!-- Skills -->
      <div class="glass-card animate-fade-in-up" style="animation-delay: 300ms">
        <h3 style="margin-bottom: 1.25rem">⚡ Extracted Skills ({{ resume.skills?.length || 0 }})</h3>
        <div v-if="resume.skills?.length" class="skills-section">
          <div class="skill-category" v-if="technicalSkills.length">
            <h4>Technical Skills</h4>
            <div class="skill-tags">
              <span v-for="skill in technicalSkills" :key="skill.id" class="skill-tag" :class="'skill-' + skill.level">
                {{ skill.name }}
                <span class="skill-level">{{ skill.level }}</span>
              </span>
            </div>
          </div>
          <div class="skill-category" v-if="softSkills.length">
            <h4>Soft Skills</h4>
            <div class="skill-tags">
              <span v-for="skill in softSkills" :key="skill.id" class="skill-tag skill-soft">
                {{ skill.name }}
              </span>
            </div>
          </div>
        </div>
        <p v-else class="text-muted">No skills detected.</p>
      </div>

      <!-- Sections detected -->
      <div class="glass-card animate-fade-in-up" style="animation-delay: 350ms">
        <h3 style="margin-bottom: 1.25rem">📋 Sections Detected</h3>
        <div class="sections-grid">
          <div v-for="(found, name) in resume.analysisResult.sections" :key="name" class="section-item">
            <span class="section-check">{{ found ? '✅' : '❌' }}</span>
            <span class="section-name">{{ formatSectionName(name) }}</span>
          </div>
        </div>
      </div>

      <!-- Suggestions -->
      <div class="glass-card animate-fade-in-up" style="animation-delay: 400ms">
        <h3 style="margin-bottom: 1.25rem">💡 AI Suggestions</h3>
        <div class="suggestions-list stagger">
          <div
            v-for="(suggestion, i) in resume.analysisResult.suggestions"
            :key="i"
            class="suggestion-item animate-fade-in-up"
            :class="'priority-' + suggestion.priority"
          >
            <div class="suggestion-header">
              <span class="badge" :class="getPriorityBadge(suggestion.priority)">
                {{ suggestion.priority }}
              </span>
              <span class="badge badge-info">{{ suggestion.type }}</span>
              <h4>{{ suggestion.title }}</h4>
            </div>
            <p>{{ suggestion.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-else class="empty-state glass-card animate-fade-in">
      <div class="empty-state-icon">❌</div>
      <h3>Analysis Not Available</h3>
      <p>This resume hasn't been analyzed yet or an error occurred.</p>
      <router-link to="/dashboard" class="btn btn-primary">← Back to Dashboard</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../composables/useApi'

const route = useRoute()
const resume = ref(null)
const loading = ref(true)
let pollTimer = null

const circumference = 2 * Math.PI * 60

const scoreOffset = computed(() => {
  const score = resume.value?.analysisResult?.atsScore || 0
  return circumference - (score / 100) * circumference
})

const scoreColor = computed(() => {
  const score = resume.value?.analysisResult?.atsScore || 0
  if (score >= 80) return '#10b981'
  if (score >= 50) return '#f59e0b'
  return '#ef4444'
})

const scoreLevel = computed(() => {
  const score = resume.value?.analysisResult?.atsScore || 0
  if (score >= 80) return { label: 'Excellent', class: 'badge badge-success' }
  if (score >= 60) return { label: 'Good', class: 'badge badge-warning' }
  if (score >= 40) return { label: 'Average', class: 'badge badge-warning' }
  return { label: 'Needs Work', class: 'badge badge-danger' }
})

const technicalSkills = computed(() =>
  (resume.value?.skills || []).filter(s => s.category === 'technical')
)
const softSkills = computed(() =>
  (resume.value?.skills || []).filter(s => s.category === 'soft')
)

async function fetchResume() {
  try {
    const res = await api.get(`/api/resume/${route.params.id}`)
    resume.value = res.data.resume

    // Poll if still processing
    if (resume.value.status === 'parsing' || resume.value.status === 'uploaded') {
      pollTimer = setTimeout(fetchResume, 3000)
    }
  } catch (err) {
    console.error('Failed to fetch resume:', err)
  } finally {
    loading.value = false
  }
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function formatEducation(level) {
  return level.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function formatBreakdownName(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function formatSectionName(name) {
  return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function getPriorityBadge(p) {
  const map = { high: 'badge-danger', medium: 'badge-warning', low: 'badge-info', info: 'badge-success' }
  return map[p] || 'badge-info'
}

onMounted(fetchResume)
onUnmounted(() => pollTimer && clearTimeout(pollTimer))
</script>

<style scoped>
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* ── Score + Summary grid ─────────────────────────────────────── */
.score-summary-grid {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.score-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
}

.score-message {
  text-align: center;
}

.summary-card h3 {
  margin-bottom: 0.75rem;
}

.summary-card p {
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 1rem;
}

.summary-meta {
  display: flex;
  gap: 1.5rem;
}

.meta-label {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  text-transform: uppercase;
}

.meta-value {
  font-weight: 600;
  font-size: var(--font-size-sm);
}

/* ── Breakdown ────────────────────────────────────────────────── */
.breakdown-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.breakdown-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.35rem;
}

.breakdown-name {
  font-weight: 600;
  font-size: var(--font-size-sm);
}

.breakdown-score {
  font-weight: 700;
  font-size: var(--font-size-sm);
  color: var(--accent-primary-light);
}

.breakdown-detail {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin-top: 0.35rem;
}

/* ── Skills ───────────────────────────────────────────────────── */
.skill-category {
  margin-bottom: 1.25rem;
}

.skill-category h4 {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-bottom: 0.75rem;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.skill-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.75rem;
  border-radius: 100px;
  font-size: var(--font-size-xs);
  font-weight: 600;
  border: 1px solid var(--border);
  background: var(--bg-glass);
}

.skill-tag.skill-advanced {
  border-color: var(--success);
  color: var(--success);
  background: var(--success-bg);
}

.skill-tag.skill-intermediate {
  border-color: var(--accent-primary);
  color: var(--accent-primary-light);
  background: var(--accent-primary-glow);
}

.skill-tag.skill-beginner {
  border-color: var(--warning);
  color: var(--warning);
  background: var(--warning-bg);
}

.skill-tag.skill-soft {
  border-color: var(--info);
  color: var(--info);
  background: var(--info-bg);
}

.skill-level {
  font-size: 10px;
  opacity: 0.7;
  text-transform: uppercase;
}

/* ── Sections ─────────────────────────────────────────────────── */
.sections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.75rem;
}

.section-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-sm);
  background: var(--bg-glass);
  font-size: var(--font-size-sm);
}

/* ── Suggestions ──────────────────────────────────────────────── */
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.suggestion-item {
  padding: 1rem 1.25rem;
  border-radius: var(--radius-md);
  background: var(--bg-glass);
  border-left: 3px solid var(--border);
}

.suggestion-item.priority-high { border-left-color: var(--danger); }
.suggestion-item.priority-medium { border-left-color: var(--warning); }
.suggestion-item.priority-low { border-left-color: var(--info); }
.suggestion-item.priority-info { border-left-color: var(--success); }

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.suggestion-header h4 {
  font-size: var(--font-size-sm);
}

.suggestion-item p {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
}

.text-muted {
  color: var(--text-muted);
}

.glass-card + .glass-card {
  margin-top: 1.5rem;
}

@media (max-width: 768px) {
  .score-summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>

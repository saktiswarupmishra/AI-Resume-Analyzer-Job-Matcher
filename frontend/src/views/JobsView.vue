<template>
  <div class="page-container">
    <div class="page-header animate-fade-in-up">
      <div class="header-row">
        <div>
          <h1 class="page-title">Job Recommendations</h1>
          <p class="page-subtitle">AI-matched jobs based on your resume skills and experience</p>
        </div>
        <div class="header-actions">
          <router-link :to="`/analysis/${$route.params.id}`" class="btn btn-secondary">← Analysis</router-link>
          <router-link to="/dashboard" class="btn btn-secondary">📊 Dashboard</router-link>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="empty-state">
      <div class="spinner"></div>
      <p style="margin-top: 1rem">Finding matching jobs...</p>
    </div>

    <!-- No matches -->
    <div v-else-if="jobs.length === 0" class="empty-state glass-card animate-fade-in">
      <div class="empty-state-icon">🔍</div>
      <h3>No Job Matches Yet</h3>
      <p>The analysis may still be in progress. Check back shortly.</p>
    </div>

    <!-- Filter bar -->
    <div v-else class="filter-bar glass-card animate-fade-in-up" style="animation-delay: 100ms">
      <div class="filter-stat">
        <strong>{{ filteredJobs.length }}</strong> jobs matched
      </div>
      <div class="filter-controls">
        <select v-model="filterCategory" class="form-input filter-select" id="filter-category">
          <option value="">All Categories</option>
          <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
        <select v-model="sortBy" class="form-input filter-select" id="filter-sort">
          <option value="score">Best Match</option>
          <option value="title">Title A-Z</option>
          <option value="company">Company A-Z</option>
        </select>
      </div>
    </div>

    <!-- Jobs list -->
    <div class="jobs-list stagger">
      <div
        v-for="job in filteredJobs"
        :key="job.id"
        class="job-card glass-card animate-fade-in-up"
      >
        <div class="job-header">
          <div class="job-title-row">
            <h3 class="job-title">{{ job.jobTitle }}</h3>
            <div class="match-badge">
              <div class="match-ring" :style="{ '--match': job.matchScore + '%', '--match-color': getMatchColor(job.matchScore) }">
                <span class="match-value">{{ Math.round(job.matchScore) }}%</span>
              </div>
            </div>
          </div>
          <div class="job-meta">
            <span class="job-company">🏢 {{ job.company }}</span>
            <span v-if="job.location" class="job-location">📍 {{ job.location }}</span>
          </div>
        </div>

        <p class="job-description" v-if="job.description">{{ job.description }}</p>

        <div class="job-skills" v-if="job.requiredSkills?.length">
          <span class="skills-label">Required:</span>
          <span v-for="skill in parseSkills(job.requiredSkills)" :key="skill" class="job-skill-tag">{{ skill }}</span>
        </div>

        <div class="job-footer">
          <span class="match-reason" v-if="job.matchReason">💡 {{ job.matchReason }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../composables/useApi'

const route = useRoute()
const jobs = ref([])
const loading = ref(true)
const filterCategory = ref('')
const sortBy = ref('score')

const categories = computed(() => {
  const cats = new Set()
  jobs.value.forEach(j => {
    if (j.category) cats.add(j.category)
  })
  return [...cats].sort()
})

const filteredJobs = computed(() => {
  let result = [...jobs.value]
  if (filterCategory.value) {
    result = result.filter(j => j.category === filterCategory.value)
  }
  if (sortBy.value === 'score') {
    result.sort((a, b) => b.matchScore - a.matchScore)
  } else if (sortBy.value === 'title') {
    result.sort((a, b) => a.jobTitle.localeCompare(b.jobTitle))
  } else if (sortBy.value === 'company') {
    result.sort((a, b) => a.company.localeCompare(b.company))
  }
  return result
})

function parseSkills(skills) {
  if (Array.isArray(skills)) return skills
  try { return JSON.parse(skills) } catch { return [] }
}

function getMatchColor(score) {
  if (score >= 70) return '#10b981'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}

async function fetchJobs() {
  loading.value = true
  try {
    const res = await api.get(`/api/analysis/jobs/${route.params.id}`)
    jobs.value = res.data.jobMatches
  } catch (err) {
    console.error('Failed to fetch jobs:', err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchJobs)
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

/* ── Filter bar ───────────────────────────────────────────────── */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
}

.filter-stat strong {
  color: var(--accent-primary-light);
}

.filter-controls {
  display: flex;
  gap: 0.75rem;
}

.filter-select {
  width: auto;
  min-width: 160px;
  padding: 0.5rem 1rem;
  font-size: var(--font-size-sm);
}

/* ── Job cards ────────────────────────────────────────────────── */
.jobs-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.job-card {
  padding: 1.5rem;
}

.job-header {
  margin-bottom: 0.75rem;
}

.job-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.job-title {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--text-primary);
}

.match-badge {
  flex-shrink: 0;
}

.match-ring {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 3px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: conic-gradient(
    var(--match-color) var(--match),
    transparent var(--match)
  );
}

.match-ring::before {
  content: '';
  position: absolute;
  inset: 3px;
  border-radius: 50%;
  background: var(--bg-secondary);
}

.match-value {
  position: relative;
  z-index: 1;
  font-size: var(--font-size-xs);
  font-weight: 800;
  color: var(--text-primary);
}

.job-meta {
  display: flex;
  gap: 1rem;
  margin-top: 0.35rem;
}

.job-company, .job-location {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.job-description {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 0.75rem;
}

.job-skills {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
}

.skills-label {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin-right: 0.25rem;
}

.job-skill-tag {
  padding: 0.2rem 0.5rem;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 600;
  background: var(--accent-primary-glow);
  color: var(--accent-primary-light);
}

.job-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.match-reason {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  font-style: italic;
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    gap: 0.75rem;
  }

  .filter-controls {
    width: 100%;
  }

  .filter-select {
    flex: 1;
  }
}
</style>

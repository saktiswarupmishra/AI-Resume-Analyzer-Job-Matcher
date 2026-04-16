<template>
  <div class="auth-page">
    <div class="auth-container animate-fade-in-up">
      <div class="auth-header">
        <div class="auth-logo">🧠</div>
        <h1 class="auth-title">Create Account</h1>
        <p class="auth-subtitle">Join ResumeAI and supercharge your career</p>
      </div>

      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label class="form-label" for="name">Full Name</label>
          <input id="name" v-model="name" type="text" class="form-input" placeholder="John Doe" required />
        </div>
        <div class="form-group">
          <label class="form-label" for="email">Email</label>
          <input id="email" v-model="email" type="email" class="form-input" placeholder="you@example.com" required />
        </div>
        <div class="form-group">
          <label class="form-label" for="password">Password</label>
          <input id="password" v-model="password" type="password" class="form-input" placeholder="Minimum 6 characters" required minlength="6" />
        </div>
        <div class="form-group">
          <label class="form-label" for="confirmPassword">Confirm Password</label>
          <input id="confirmPassword" v-model="confirmPassword" type="password" class="form-input" placeholder="••••••••" required />
        </div>
        <button id="btn-register" type="submit" class="btn btn-primary btn-lg auth-btn" :disabled="loading">
          <span v-if="loading" class="spinner spinner-sm"></span>
          <span v-else>Create Account</span>
        </button>
      </form>

      <p class="auth-footer">
        Already have an account? <router-link to="/login">Sign in</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { register } = useAuth()

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match.'
    return
  }

  loading.value = true
  try {
    await register(name.value, email.value, password.value)
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.error || 'Registration failed.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.auth-container {
  width: 100%;
  max-width: 420px;
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-logo {
  font-size: 48px;
  margin-bottom: 1rem;
  animation: pulse 3s ease infinite;
}

.auth-title {
  font-size: var(--font-size-3xl);
  font-weight: 800;
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.auth-subtitle {
  color: var(--text-secondary);
}

.auth-form {
  background: var(--bg-glass);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 2rem;
  backdrop-filter: blur(20px);
}

.auth-btn {
  width: 100%;
  margin-top: 0.5rem;
}

.auth-footer {
  text-align: center;
  margin-top: 1.5rem;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}
</style>

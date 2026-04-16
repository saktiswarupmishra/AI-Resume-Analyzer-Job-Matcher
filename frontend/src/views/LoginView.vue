<template>
  <div class="auth-page">
    <div class="auth-container animate-fade-in-up">
      <div class="auth-header">
        <div class="auth-logo">🧠</div>
        <h1 class="auth-title">Welcome Back</h1>
        <p class="auth-subtitle">Sign in to your ResumeAI account</p>
      </div>

      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label class="form-label" for="email">Email</label>
          <input id="email" v-model="email" type="email" class="form-input" placeholder="you@example.com" required />
        </div>
        <div class="form-group">
          <label class="form-label" for="password">Password</label>
          <input id="password" v-model="password" type="password" class="form-input" placeholder="••••••••" required />
        </div>
        <button id="btn-login" type="submit" class="btn btn-primary btn-lg auth-btn" :disabled="loading">
          <span v-if="loading" class="spinner spinner-sm"></span>
          <span v-else>Sign In</span>
        </button>
      </form>

      <p class="auth-footer">
        Don't have an account? <router-link to="/register">Create one</router-link>
      </p>


    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { login } = useAuth()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)



async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await login(email.value, password.value)
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed. Please try again.'
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

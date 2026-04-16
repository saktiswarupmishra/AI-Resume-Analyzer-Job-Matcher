import { reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from './useApi'

const state = reactive({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token') || null,
})

export function useAuth() {
  const router = useRouter()

  const isLoggedIn = computed(() => !!state.token)
  const user = computed(() => state.user)

  async function login(email, password) {
    const res = await api.post('/api/auth/login', { email, password })
    state.token = res.data.token
    state.user = res.data.user
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    return res.data
  }

  async function register(name, email, password) {
    const res = await api.post('/api/auth/register', { name, email, password })
    state.token = res.data.token
    state.user = res.data.user
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    return res.data
  }

  function logout() {
    state.token = null
    state.user = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  return { isLoggedIn, user, login, register, logout }
}

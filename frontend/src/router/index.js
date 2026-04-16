import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
    meta: { guest: true },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { auth: true },
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('../views/UploadView.vue'),
    meta: { auth: true },
  },
  {
    path: '/analysis/:id',
    name: 'Analysis',
    component: () => import('../views/AnalysisView.vue'),
    meta: { auth: true },
  },
  {
    path: '/jobs/:id',
    name: 'Jobs',
    component: () => import('../views/JobsView.vue'),
    meta: { auth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Auth guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.auth && !token) {
    next('/login')
  } else if (to.meta.guest && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router

<template>
  <div class="app-layout" :class="{ 'has-sidebar': isLoggedIn }">
    <!-- Sidebar -->
    <aside v-if="isLoggedIn" class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">🧠</div>
        <span class="brand-text">ResumeAI</span>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-item" active-class="active" id="nav-dashboard">
          <span class="nav-icon">📊</span>
          <span class="nav-label">Dashboard</span>
        </router-link>
        <router-link to="/upload" class="nav-item" active-class="active" id="nav-upload">
          <span class="nav-icon">📄</span>
          <span class="nav-label">Upload Resume</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ user?.name?.charAt(0) || 'U' }}</div>
          <div class="user-details">
            <div class="user-name">{{ user?.name }}</div>
            <div class="user-email">{{ user?.email }}</div>
          </div>
        </div>
        <button class="btn btn-secondary btn-sm" @click="logout" id="btn-logout">
          🚪 Logout
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { useAuth } from './composables/useAuth'

const { isLoggedIn, user, logout } = useAuth()
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* ── Sidebar ───────────────────────────────────────────────────── */
.sidebar {
  width: 260px;
  background: rgba(17, 24, 39, 0.95);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 100;
  animation: slideInLeft 0.4s ease;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  margin-bottom: 2rem;
}

.brand-icon {
  font-size: 28px;
  animation: pulse 3s ease infinite;
}

.brand-text {
  font-size: var(--font-size-xl);
  font-weight: 800;
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-weight: 500;
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
  text-decoration: none;
}

.nav-item:hover {
  background: var(--bg-glass);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--accent-primary-glow);
  color: var(--accent-primary-light);
}

.nav-icon {
  font-size: 18px;
}

/* ── Sidebar footer ────────────────────────────────────────────── */
.sidebar-footer {
  border-top: 1px solid var(--border);
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: var(--font-size-sm);
  color: white;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 600;
  font-size: var(--font-size-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── Main content ──────────────────────────────────────────────── */
.main-content {
  flex: 1;
  min-height: 100vh;
}

.has-sidebar .main-content {
  margin-left: 260px;
}

/* ── Page transitions ──────────────────────────────────────────── */
.page-enter-active {
  animation: fadeInUp 0.35s ease;
}

.page-leave-active {
  animation: fadeIn 0.15s ease reverse;
}

/* ── Responsive ────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .sidebar {
    width: 72px;
    padding: 1rem 0.5rem;
  }

  .brand-text,
  .nav-label,
  .user-details {
    display: none;
  }

  .has-sidebar .main-content {
    margin-left: 72px;
  }

  .nav-item {
    justify-content: center;
    padding: 0.75rem;
  }

  .user-info {
    justify-content: center;
  }

  .sidebar-footer .btn {
    padding: 0.5rem;
    font-size: 0;
  }

  .sidebar-footer .btn::after {
    content: '🚪';
    font-size: 16px;
  }
}
</style>

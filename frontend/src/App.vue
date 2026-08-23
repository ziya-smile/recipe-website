<script setup>
import { useTheme } from '../composables/useTheme'
import ChatBot from '../components/ChatBot.vue'

const { theme, toggleTheme } = useTheme()
</script>

<template>
  <div class="site">
    <header class="site-header">
      <div class="site-header-left">
        <RouterLink class="logo" to="/">
          <span class="logo-emoji">🍳</span>
          <span>Fun recipes</span>
        </RouterLink>
        <nav class="nav-links">
          <RouterLink to="/">Home</RouterLink>
          <RouterLink to="/recipes">Recipes</RouterLink>
        </nav>
      </div>
      <div class="header-right">
        <button
          class="theme-toggle"
          :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
          @click="toggleTheme"
        >
          <svg v-if="theme === 'dark'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
          </svg>
        </button>
      </div>
    </header>
    <RouterView />
    <ChatBot />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ChatBot from './components/ChatBot.vue'

const isDark = ref(false)

function toggleTheme() {
  isDark.value = !isDark.value
  const theme = isDark.value ? 'dark' : 'light'
  document.documentElement.classList.remove('light', 'dark')
  document.documentElement.classList.add(theme)
  localStorage.setItem('theme', theme)
}

onMounted(() => {
  const saved = localStorage.getItem('theme')
  if (saved) {
    isDark.value = saved === 'dark'
    document.documentElement.classList.add(saved)
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }
})
</script>

<template>
  <div class="site">
    <header class="site-header">
      <RouterLink class="logo" to="/">Fun recipes</RouterLink>
      <nav class="nav-links">
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/recipes">Recipes</RouterLink>
      </nav>
      <button class="theme-toggle-btn" @click="toggleTheme" :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'">
        <span v-if="isDark">☀️</span>
        <span v-else>🌙</span>
      </button>
    </header>
    <RouterView />
    <ChatBot />
  </div>
</template>

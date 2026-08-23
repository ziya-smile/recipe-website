<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import ChatBot from './components/ChatBot.vue'
import { fetchRecipes } from './api'
import { supabase } from './supabase'

const router = useRouter()
const isDark = ref(false)
const searchQuery = ref('')
const suggestions = ref([])
const showSuggestions = ref(false)
const searchWrapperRef = ref(null)
const user = ref(null)

function setTheme(theme) {
  isDark.value = theme === 'dark'
  document.documentElement.classList.remove('light', 'dark')
  document.documentElement.classList.add(theme)
  localStorage.setItem('theme', theme)
}

onMounted(async () => {
  const saved = localStorage.getItem('theme')
  if (saved) {
    isDark.value = saved === 'dark'
    document.documentElement.classList.add(saved)
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }

  document.addEventListener('click', handleClickOutside)

  // Get initial session
  const { data: { session } } = await supabase.auth.getSession()
  user.value = session?.user || null

  // Listen for auth state changes
  supabase.auth.onAuthStateChange((_event, session) => {
    user.value = session?.user || null
  })
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

async function handleSignOut() {
  await supabase.auth.signOut()
  router.push('/')
}

function handleClickOutside(e) {
  if (searchWrapperRef.value && !searchWrapperRef.value.contains(e.target)) {
    showSuggestions.value = false
  }
}

function handleFocus() {
  if (suggestions.value.length) {
    showSuggestions.value = true
  }
}

let timeout = null
watch(searchQuery, (val) => {
  clearTimeout(timeout)
  if (!val.trim()) {
    suggestions.value = []
    showSuggestions.value = false
    return
  }
  timeout = setTimeout(async () => {
    try {
      const res = await fetchRecipes(val.trim())
      suggestions.value = res.slice(0, 5)
      showSuggestions.value = true
    } catch {
      suggestions.value = []
    }
  }, 200)
})

function selectRecipe(recipe) {
  searchQuery.value = ''
  showSuggestions.value = false
  router.push(`/recipes/${recipe.id}`)
}
</script>

<template>
  <div class="site">
    <header class="site-header">
      <RouterLink class="logo" to="/">Fun recipes</RouterLink>
      <nav class="nav-links">
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/recipes">Recipes</RouterLink>
      </nav>
      <div class="header-right">
        <div class="header-search" ref="searchWrapperRef">
          <svg class="header-search-icon" viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input
            type="search"
            class="header-search-input"
            placeholder="Search recipes..."
            v-model="searchQuery"
            @focus="handleFocus"
          />
          <div v-if="showSuggestions && suggestions.length" class="suggestions-dropdown">
            <div
              v-for="recipe in suggestions"
              :key="recipe.id"
              class="suggestion-item"
              @click="selectRecipe(recipe)"
            >
              <img v-if="recipe.image_url" :src="recipe.image_url" class="suggestion-thumb" alt="" />
              <div v-else class="suggestion-thumb-placeholder">🍽️</div>
              <div class="suggestion-info">
                <div class="suggestion-title">{{ recipe.title }}</div>
                <div class="suggestion-desc">{{ recipe.description }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="auth-nav">
          <template v-if="user">
            <span class="user-email" :title="user.email">{{ user.email }}</span>
            <button class="auth-btn logout-btn" @click="handleSignOut">Sign Out</button>
          </template>
          <template v-else>
            <RouterLink to="/auth" class="auth-btn login-btn">Sign In</RouterLink>
          </template>
        </div>

        <div class="theme-toggle">
          <button class="theme-option" :class="{ active: !isDark }" @click="setTheme('light')">
            <span>☀️</span> Light
          </button>
          <button class="theme-option" :class="{ active: isDark }" @click="setTheme('dark')">
            <span>🌙</span> Dark
          </button>
        </div>
      </div>
    </header>
    <RouterView />
    <ChatBot />
  </div>
</template>

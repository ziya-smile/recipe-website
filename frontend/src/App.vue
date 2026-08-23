<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import ChatBot from './components/ChatBot.vue'
import { fetchRecipes } from './api'
import { supabase } from './supabase'
import { useFavorites } from './composables/useFavorites'

const router = useRouter()
const isDark = ref(false)
const searchQuery = ref('')
const suggestions = ref([])
const showSuggestions = ref(false)
const showUserMenu = ref(false)
const searchWrapperRef = ref(null)
const userMenuRef = ref(null)
const user = ref(null)

const { favoritesCount, isLoggedIn } = useFavorites()

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
  showUserMenu.value = false
  await supabase.auth.signOut()
  router.push('/')
}

function handleClickOutside(e) {
  if (searchWrapperRef.value && !searchWrapperRef.value.contains(e.target)) {
    showSuggestions.value = false
  }
  if (userMenuRef.value && !userMenuRef.value.contains(e.target)) {
    showUserMenu.value = false
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
            <div class="user-menu-container" ref="userMenuRef">
              <button class="auth-btn user-menu-toggle" @click="showUserMenu = !showUserMenu">
                <span>👤</span>
                <span class="user-email-truncate" :title="user.email">{{ user.email }}</span>
                <span class="dropdown-caret">▼</span>
              </button>
              <div v-if="showUserMenu" class="user-dropdown-menu">
                <div class="dropdown-user-info">
                  <span class="dropdown-label">Signed in as</span>
                  <span class="dropdown-email" :title="user.email">{{ user.email }}</span>
                </div>
                <div class="dropdown-divider"></div>
                <RouterLink
                  v-if="isLoggedIn"
                  to="/favorites"
                  class="dropdown-item saved-favorites-item"
                  @click="showUserMenu = false"
                >
                  <span>❤️ Saved Recipes</span>
                  <span class="favorites-count-badge">{{ favoritesCount }}</span>
                </RouterLink>
                <div class="dropdown-divider"></div>
                <button class="dropdown-item logout-action-btn" @click="handleSignOut">
                  <span>🚪</span> Sign Out
                </button>
              </div>
            </div>
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

<style scoped>
.user-menu-container {
  position: relative;
  display: inline-block;
}

.user-menu-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 220px;
  cursor: pointer;
}

.user-email-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-caret {
  font-size: 10px;
  opacity: 0.7;
}

.user-dropdown-menu {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  width: 240px;
  background: var(--card-bg, #1a1d26);
  border: 1px solid var(--card-border, #2a2e3d);
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  z-index: 100;
  overflow: hidden;
  animation: dropdownFadeIn 0.15s ease;
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-user-info {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.02);
}

.dropdown-label {
  display: block;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted, #94a3b8);
  margin-bottom: 2px;
}

.dropdown-email {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text, #f8fafc);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-divider {
  height: 1px;
  background: var(--card-border, #2a2e3d);
  margin: 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 10px 16px;
  font-size: 13px;
  color: var(--text, #f8fafc);
  background: transparent;
  border: none;
  text-align: left;
  text-decoration: none;
  box-sizing: border-box;
}

.saved-favorites-item {
  background: rgba(255, 255, 255, 0.02);
  transition: background 0.15s;
}

.saved-favorites-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.favorites-count-badge {
  background: var(--primary, #aa3bff);
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
}

.logout-action-btn {
  cursor: pointer;
  color: #f87171;
  transition: background 0.15s;
}

.logout-action-btn:hover {
  background: rgba(248, 113, 113, 0.1);
}
</style>

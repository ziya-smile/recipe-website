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
              <img v-if="recipe.image || recipe.image_url" :src="recipe.image || recipe.image_url" class="suggestion-thumb" alt="" />
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
              <button 
                class="auth-btn user-menu-toggle" 
                :class="{ 'menu-open': showUserMenu }"
                @click="showUserMenu = !showUserMenu"
              >
                <div class="user-avatar-badge">
                  {{ user.email ? user.email.charAt(0).toUpperCase() : '👤' }}
                </div>
                <span class="user-email-truncate" :title="user.email">{{ user.email }}</span>
                <svg class="dropdown-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="m6 9 6 6 6-6"/>
                </svg>
              </button>
              
              <div v-if="showUserMenu" class="user-dropdown-menu">
                <div class="dropdown-user-info">
                  <div class="dropdown-user-avatar-large">
                    {{ user.email ? user.email.charAt(0).toUpperCase() : '👤' }}
                  </div>
                  <div class="dropdown-user-text">
                    <span class="dropdown-label">Signed in as</span>
                    <span class="dropdown-email" :title="user.email">{{ user.email }}</span>
                  </div>
                </div>

                <div class="dropdown-divider"></div>

                <div class="dropdown-links-group">
                  <RouterLink
                    v-if="isLoggedIn"
                    to="/favorites"
                    class="dropdown-item saved-favorites-item"
                    @click="showUserMenu = false"
                  >
                    <div class="dropdown-item-content">
                      <span class="dropdown-icon-wrapper">❤️</span>
                      <span>Saved Recipes</span>
                    </div>
                    <span class="favorites-count-badge">{{ favoritesCount }}</span>
                  </RouterLink>
                </div>

                <div class="dropdown-divider"></div>

                <button class="dropdown-item logout-action-btn" @click="handleSignOut">
                  <div class="dropdown-item-content">
                    <span class="dropdown-icon-wrapper logout-icon">🚪</span>
                    <span>Sign Out</span>
                  </div>
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
  gap: 8px;
  max-width: 240px;
  cursor: pointer;
  background: var(--card-bg, rgba(255, 255, 255, 0.05));
  border: 1px solid var(--card-border, rgba(255, 255, 255, 0.1));
  padding: 6px 12px 6px 6px;
  border-radius: 20px;
  transition: all 0.2s ease;
}

.user-menu-toggle:hover,
.user-menu-toggle.menu-open {
  background: var(--card-border, rgba(255, 255, 255, 0.1));
  border-color: var(--primary, #aa3bff);
}

.user-avatar-badge {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary, #aa3bff), #7928ca);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.user-email-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 500;
}

.dropdown-chevron {
  opacity: 0.6;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.user-menu-toggle.menu-open .dropdown-chevron {
  transform: rotate(180deg);
}

.user-dropdown-menu {
  position: absolute;
  right: 0;
  top: calc(100% + 10px);
  width: 270px;
  background: var(--card-bg, #1a1d26);
  border: 1px solid var(--card-border, #2a2e3d);
  border-radius: 14px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
  z-index: 100;
  overflow: hidden;
  animation: dropdownFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-8px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.dropdown-user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0));
}

.dropdown-user-avatar-large {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary, #aa3bff), #7928ca);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(170, 59, 255, 0.3);
}

.dropdown-user-text {
  overflow: hidden;
}

.dropdown-label {
  display: block;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-muted, #94a3b8);
  margin-bottom: 2px;
  font-weight: 600;
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

.dropdown-links-group {
  padding: 6px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 10px 12px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text, #f8fafc);
  background: transparent;
  border: none;
  border-radius: 8px;
  text-align: left;
  text-decoration: none;
  box-sizing: border-box;
  cursor: pointer;
  transition: all 0.15s ease;
}

.dropdown-item-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dropdown-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  font-size: 13px;
}

.saved-favorites-item:hover {
  background: rgba(255, 255, 255, 0.07);
  color: var(--primary, #aa3bff);
}

.favorites-count-badge {
  background: var(--primary, #aa3bff);
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(170, 59, 255, 0.3);
}

.logout-action-btn {
  margin: 6px;
  width: calc(100% - 12px);
  color: #f87171;
  transition: all 0.15s ease;
}

.logout-action-btn:hover {
  background: rgba(248, 113, 113, 0.1);
  color: #ef4444;
}

.logout-icon {
  background: rgba(248, 113, 113, 0.1);
}
</style>

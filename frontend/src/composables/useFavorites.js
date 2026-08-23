import { ref, computed, onMounted } from 'vue'
import { supabase } from '../supabase'

const STORAGE_KEY = 'recipe_website_favorites'

function loadFavorites() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return new Set()
    const parsed = JSON.parse(raw)
    return new Set(Array.isArray(parsed) ? parsed : [])
  } catch {
    return new Set()
  }
}

function saveFavorites(favoritesSet) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...favoritesSet]))
  } catch {
    // Ignore storage quota or disabled localStorage errors
  }
}

// Shared singleton state across components
const favorites = ref(loadFavorites())
const user = ref(null)

// Initialize user and auth listener
supabase.auth.getSession().then(({ data }) => {
  user.value = data.session?.user ?? null
})

supabase.auth.onAuthStateChange((_, session) => {
  user.value = session?.user ?? null
})

export function useFavorites() {
  const isLoggedIn = computed(() => !!user.value)

  function isFavorite(id) {
    if (!isLoggedIn.value) return false
    if (id === undefined || id === null) return false
    return favorites.value.has(Number(id))
  }

  function toggleFavorite(id) {
    if (!isLoggedIn.value) return
    if (id === undefined || id === null) return
    const numId = Number(id)
    const next = new Set(favorites.value)
    if (next.has(numId)) {
      next.delete(numId)
    } else {
      next.add(numId)
    }
    favorites.value = next
    saveFavorites(next)
  }

  const favoritesCount = computed(() => (isLoggedIn.value ? favorites.value.size : 0))

  return {
    favorites,
    favoritesCount,
    isLoggedIn,
    isFavorite,
    toggleFavorite,
  }
}

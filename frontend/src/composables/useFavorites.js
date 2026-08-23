import { ref, computed } from 'vue'
import { supabase } from '../supabase'

const favorites = ref(new Set())
const user = ref(null)

async function fetchUserFavorites(userId) {
  try {
    const { data, error } = await supabase
      .from('favorites')
      .select('recipe_id')
      .eq('user_id', userId)
    
    if (error) throw error
    if (data) {
      favorites.value = new Set(data.map(row => Number(row.recipe_id)))
    }
  } catch (err) {
    console.error('Error fetching favorites:', err)
  }
}

// Initialize user and auth listener
supabase.auth.getSession().then(({ data }) => {
  user.value = data.session?.user ?? null
  if (user.value) {
    fetchUserFavorites(user.value.id)
  }
})

supabase.auth.onAuthStateChange((_, session) => {
  user.value = session?.user ?? null
  if (user.value) {
    fetchUserFavorites(user.value.id)
  } else {
    favorites.value = new Set()
  }
})

export function useFavorites() {
  const isLoggedIn = computed(() => !!user.value)

  function isFavorite(id) {
    if (!isLoggedIn.value) return false
    if (id === undefined || id === null) return false
    return favorites.value.has(Number(id))
  }

  async function toggleFavorite(id) {
    if (!isLoggedIn.value || !user.value) return
    if (id === undefined || id === null) return
    const numId = Number(id)
    const next = new Set(favorites.value)
    
    try {
      if (next.has(numId)) {
        next.delete(numId)
        favorites.value = next
        const { error } = await supabase
          .from('favorites')
          .delete()
          .eq('user_id', user.value.id)
          .eq('recipe_id', numId)
        if (error) {
          next.add(numId)
          favorites.value = new Set(next)
          throw error
        }
      } else {
        next.add(numId)
        favorites.value = next
        const { error } = await supabase
          .from('favorites')
          .insert({ user_id: user.value.id, recipe_id: numId })
        if (error) {
          next.delete(numId)
          favorites.value = new Set(next)
          throw error
        }
      }
    } catch (err) {
      console.error('Error toggling favorite:', err)
    }
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

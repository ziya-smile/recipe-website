<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchRecipes } from '../api'
import RecipeCard from '../components/RecipeCard.vue'
import { useFavorites } from '../composables/useFavorites'

const recipes = ref([])
const status = ref('Loading favorite recipes...')
const { favorites, isLoggedIn } = useFavorites()

const favoriteRecipes = computed(() => {
  return recipes.value.filter((recipe) => favorites.value.has(Number(recipe.id)))
})

onMounted(async () => {
  try {
    recipes.value = await fetchRecipes()
    status.value = ''
  } catch (err) {
    status.value = 'Could not load recipes: ' + err.message
  }
})
</script>

<template>
  <main class="section">
    <div class="section-heading">
      <h1>Saved recipes</h1>
    </div>

    <p v-if="status" class="status">{{ status }}</p>

    <div v-else-if="!isLoggedIn" class="empty-state">
      <p class="empty-title">Please sign in</p>
      <p class="empty-text">Sign in to view your saved favorite recipes.</p>
      <RouterLink to="/auth" class="button">Sign In</RouterLink>
    </div>

    <div v-else-if="favoriteRecipes.length === 0" class="empty-state">
      <p class="empty-title">No saved recipes yet</p>
      <p class="empty-text">Browse recipes and click the heart icon to save them here.</p>
      <RouterLink to="/recipes" class="button">Browse Recipes</RouterLink>
    </div>

    <ul v-else class="recipe-grid">
      <RecipeCard
        v-for="recipe in favoriteRecipes"
        :key="recipe.id"
        :recipe="recipe"
      />
    </ul>
  </main>
</template>

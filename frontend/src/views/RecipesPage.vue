<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchRecipes } from '../api'
import { useFavorites } from '../composables/useFavorites'
import RecipeCard from '../components/RecipeCard.vue'

const recipes = ref([])
const searchQuery = ref('')
const activeTab = ref('all')
const status = ref('Loading recipes...')
const filterCategory = ref('')
const filterDifficulty = ref('')
const filterCookTime = ref('')

const { isFavorite } = useFavorites()

const savedCount = computed(
  () => recipes.value.filter((recipe) => isFavorite(recipe.id)).length
)

const categories = computed(() => {
  const set = new Set()
  recipes.value.forEach((r) => { if (r.category) set.add(r.category) })
  return [...set].sort()
})

const filteredRecipes = computed(() => {
  let list = recipes.value
  if (activeTab.value === 'favorites') {
    list = list.filter((r) => isFavorite(r.id))
  }
  if (filterCategory.value) {
    list = list.filter((r) => r.category === filterCategory.value)
  }
  if (filterDifficulty.value) {
    list = list.filter((r) => r.difficulty === filterDifficulty.value)
  }
  if (filterCookTime.value) {
    list = list.filter((r) => r.cook_time != null && r.cook_time <= Number(filterCookTime.value))
  }
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter((recipe) => {
      const titleMatch = recipe.title?.toLowerCase().includes(q)
      const descMatch = recipe.description?.toLowerCase().includes(q)
      const ingMatch = recipe.ingredients?.some((ing) =>
        ing.toLowerCase().includes(q)
      )
      return titleMatch || descMatch || ingMatch
    })
  }
  return list
})

const hasFilters = computed(
  () => filterCategory.value || filterDifficulty.value || filterCookTime.value
)

function clearSearch() {
  searchQuery.value = ''
}

function clearFilters() {
  filterCategory.value = ''
  filterDifficulty.value = ''
  filterCookTime.value = ''
}

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
      <h1>All recipes</h1>
    </div>

    <div class="recipes-toolbar">
      <div class="filter-tabs" role="tablist" aria-label="Recipe filters">
        <button
          type="button"
          class="tab-btn"
          :class="{ 'is-active': activeTab === 'all' }"
          role="tab"
          :aria-selected="activeTab === 'all'"
          @click="activeTab = 'all'"
        >
          All recipes ({{ recipes.length }})
        </button>
        <button
          type="button"
          class="tab-btn"
          :class="{ 'is-active': activeTab === 'favorites' }"
          role="tab"
          :aria-selected="activeTab === 'favorites'"
          @click="activeTab = 'favorites'"
        >
          ❤️ Saved ({{ savedCount }})
        </button>
      </div>

      <div class="filter-row">
        <select v-model="filterCategory" class="filter-select" aria-label="Filter by category">
          <option value="">📂 All categories</option>
          <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
        <select v-model="filterDifficulty" class="filter-select" aria-label="Filter by difficulty">
          <option value="">📊 Any difficulty</option>
          <option value="easy">🟢 Easy</option>
          <option value="medium">🟡 Medium</option>
          <option value="hard">🔴 Hard</option>
        </select>
        <select v-model="filterCookTime" class="filter-select" aria-label="Filter by cook time">
          <option value="">⏱️ Any time</option>
          <option value="15">Under 15 min</option>
          <option value="30">Under 30 min</option>
          <option value="60">Under 1 hour</option>
        </select>
        <button v-if="hasFilters" type="button" class="reset-btn" @click="clearFilters">
          Clear filters
        </button>
      </div>

      <div class="search-bar">
        <div class="search-input-wrapper">
          <svg
            class="search-icon"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.3-4.3" />
          </svg>
          <input
            v-model="searchQuery"
            type="search"
            :placeholder="activeTab === 'favorites' ? 'Search saved recipes...' : 'Search by recipe name or ingredient...'"
            aria-label="Search recipes"
            class="search-input"
          />
          <button
            v-if="searchQuery"
            type="button"
            class="search-clear-btn"
            aria-label="Clear search"
            @click="clearSearch"
          >
            ✕
          </button>
        </div>
        <p v-if="searchQuery && !status" class="search-meta">
          Showing {{ filteredRecipes.length }} of {{ activeTab === 'favorites' ? savedCount : recipes.length }} {{ filteredRecipes.length === 1 ? 'recipe' : 'recipes' }}
        </p>
      </div>
    </div>

    <p v-if="status" class="status">{{ status }}</p>

    <!-- Empty state for empty saved list -->
    <div
      v-else-if="activeTab === 'favorites' && savedCount === 0"
      class="empty-state"
    >
      <p class="empty-title">No saved recipes yet</p>
      <p class="empty-text">
        Click the heart icon (❤️) on any recipe card to save it for quick access here.
      </p>
      <button type="button" class="button" @click="activeTab = 'all'">
        Browse all recipes
      </button>
    </div>

    <!-- Empty state when no recipes exist yet -->
    <div v-else-if="recipes.length === 0" class="empty-state">
      <p class="empty-title">No recipes yet</p>
      <p class="empty-text">Recipes added from the admin panel show up here.</p>
    </div>

    <!-- Empty state for search/filter with zero matches -->
    <div v-else-if="filteredRecipes.length === 0" class="empty-state">
      <p class="empty-title">No recipes found</p>
      <p class="empty-text">
        We couldn't find any recipes matching your filters{{ searchQuery ? ' and "' + searchQuery + '"' : '' }}.
      </p>
      <button v-if="searchQuery || hasFilters" type="button" class="button" @click="clearSearch(); clearFilters()">
        Clear all
      </button>
    </div>

    <ul v-else class="recipe-grid">
      <RecipeCard
        v-for="recipe in filteredRecipes"
        :key="recipe.id"
        :recipe="recipe"
      />
    </ul>
  </main>
</template>

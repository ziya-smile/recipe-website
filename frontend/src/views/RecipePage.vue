<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { fetchRecipe } from '../api'
import { useFavorites } from '../composables/useFavorites'

const route = useRoute()
const recipe = ref(null)
const status = ref('Loading recipe...')
const imgError = ref(false)
const checkedIngredients = ref(new Set())
const completedSteps = ref(new Set())
const copyStatus = ref('')
const unitSystem = ref('metric') // 'metric' or 'imperial'
const { isFavorite, toggleFavorite } = useFavorites()

function getIngredientKey(item) {
  if (typeof item === 'string') return item
  return `${item.amount || ''}-${item.unit || ''}-${item.name}`
}

function toggleIngredient(item) {
  const key = getIngredientKey(item)
  if (checkedIngredients.value.has(key)) {
    checkedIngredients.value.delete(key)
  } else {
    checkedIngredients.value.add(key)
  }
}

function isChecked(item) {
  return checkedIngredients.value.has(getIngredientKey(item))
}

function toggleStep(idx) {
  if (completedSteps.value.has(idx)) {
    completedSteps.value.delete(idx)
  } else {
    completedSteps.value.add(idx)
  }
}

function resetChecklist() {
  checkedIngredients.value.clear()
  completedSteps.value.clear()
}

function parseNumericAmount(amount) {
  if (amount === undefined || amount === null || amount === '') return NaN
  const str = String(amount).trim()
  if (str.includes('/')) {
    const parts = str.split(/\s+/)
    let total = 0
    for (const part of parts) {
      if (part.includes('/')) {
        const sub = part.split('/')
        const num = parseFloat(sub[0])
        const den = parseFloat(sub[1])
        if (!isNaN(num) && !isNaN(den) && den !== 0) {
          total += num / den
        }
      } else {
        const num = parseFloat(part)
        if (!isNaN(num)) {
          total += num
        }
      }
    }
    return isNaN(total) ? NaN : total
  }
  return parseFloat(str)
}

const convertedIngredients = computed(() => {
  if (!recipe.value?.ingredients) return []
  return recipe.value.ingredients.map((ing) => {
    if (typeof ing === 'string') {
      return { amount: '', unit: '', name: ing }
    }
    let amount = ing.amount
    let unit = (ing.unit || '').toLowerCase().trim()
    let name = ing.name

    const numAmount = parseNumericAmount(amount)

    if (!isNaN(numAmount)) {
      if (unitSystem.value === 'imperial') {
        if (['g', 'gram', 'grams'].includes(unit)) {
          amount = (numAmount * 0.035274).toFixed(1)
          unit = 'oz'
        } else if (['kg', 'kilogram', 'kilograms'].includes(unit)) {
          amount = (numAmount * 2.20462).toFixed(1)
          unit = 'lbs'
        } else if (['ml', 'milliliter', 'milliliters'].includes(unit)) {
          if (numAmount >= 240) {
            amount = (numAmount / 240).toFixed(2)
            unit = 'cups'
          } else {
            amount = (numAmount * 0.033814).toFixed(1)
            unit = 'fl oz'
          }
        } else if (['l', 'liter', 'liters'].includes(unit)) {
          amount = (numAmount * 2.11338).toFixed(1)
          unit = 'pints'
        } else if (['°c', 'celsius', 'c'].includes(unit)) {
          amount = Math.round((numAmount * 9/5) + 32)
          unit = '°F'
        }
      } else {
        // Imperial to Metric conversion
        if (['oz', 'ounce', 'ounces'].includes(unit)) {
          amount = (numAmount * 28.3495).toFixed(0)
          unit = 'g'
        } else if (['lb', 'lbs', 'pound', 'pounds'].includes(unit)) {
          amount = (numAmount * 0.453592).toFixed(2)
          unit = 'kg'
        } else if (['cup', 'cups'].includes(unit)) {
          amount = Math.round(numAmount * 240)
          unit = 'ml'
        } else if (['tbsp', 'tablespoon', 'tablespoons'].includes(unit)) {
          amount = Math.round(numAmount * 15)
          unit = 'ml'
        } else if (['tsp', 'teaspoon', 'teaspoons'].includes(unit)) {
          amount = Math.round(numAmount * 5)
          unit = 'ml'
        } else if (['fl oz', 'fluid ounce', 'fluid ounces'].includes(unit)) {
          amount = Math.round(numAmount * 29.5735)
          unit = 'ml'
        } else if (['°f', 'fahrenheit', 'f'].includes(unit)) {
          amount = Math.round((numAmount - 32) * 5/9)
          unit = '°C'
        }
      }
    }

    return {
      original: ing,
      amount,
      unit,
      name,
    }
  })
})

async function copyIngredients() {
  if (!recipe.value?.ingredients?.length) return
  const text = `${recipe.value.title} - Ingredients:\n` +
    convertedIngredients.value
      .map((i) => `• ${i.amount ? i.amount + ' ' : ''}${i.unit ? i.unit + ' ' : ''}${i.name}`)
      .join('\n')
  try {
    await navigator.clipboard.writeText(text)
    copyStatus.value = '✓ Copied!'
    setTimeout(() => {
      copyStatus.value = ''
    }, 2000)
  } catch {
    copyStatus.value = 'Error copying'
    setTimeout(() => {
      copyStatus.value = ''
    }, 2000)
  }
}

watch(
  () => route.params.id,
  async (id) => {
    recipe.value = null
    status.value = 'Loading recipe...'
    imgError.value = false
    checkedIngredients.value.clear()
    completedSteps.value.clear()
    copyStatus.value = ''
    unitSystem.value = 'metric'
    try {
      recipe.value = await fetchRecipe(id)
      status.value = ''
    } catch (err) {
      status.value = err.message
    }
  },
  { immediate: true },
)
</script>

<template>
  <main class="section recipe-detail">
    <div class="recipe-top-bar">
      <RouterLink class="back" to="/recipes">← All recipes</RouterLink>
      <button
        v-if="recipe"
        type="button"
        class="fav-toggle-btn"
        :class="{ 'is-active': isFavorite(recipe.id) }"
        :aria-label="isFavorite(recipe.id) ? 'Remove from saved' : 'Save recipe'"
        @click="toggleFavorite(recipe.id)"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          :fill="isFavorite(recipe.id) ? 'currentColor' : 'none'"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
        </svg>
        <span>{{ isFavorite(recipe.id) ? 'Saved' : 'Save recipe' }}</span>
      </button>
    </div>
    <p v-if="status" class="status">{{ status }}</p>
    <article v-else-if="recipe">
      <div class="recipe-photo">
        <img
          v-if="recipe.image && !imgError"
          :src="recipe.image"
          :alt="recipe.title"
          @error="imgError = true"
        />
        <div v-else class="photo-placeholder">
          <span>🍳 Photo coming soon</span>
        </div>
      </div>
      <h1 class="recipe-title">{{ recipe.title }}</h1>
      <p class="recipe-description">{{ recipe.description }}</p>

      <div class="recipe-block">
        <div class="recipe-section-header">
          <h2>Ingredients</h2>
          <div class="recipe-actions">
            <div class="unit-toggle-group">
              <button
                type="button"
                :class="{ active: unitSystem === 'metric' }"
                @click="unitSystem = 'metric'"
              >
                Metric
              </button>
              <button
                type="button"
                :class="{ active: unitSystem === 'imperial' }"
                @click="unitSystem = 'imperial'"
              >
                Imperial
              </button>
            </div>
            <button
              type="button"
              class="copy-btn"
              :class="{ 'copy-btn-success': copyStatus === '✓ Copied!' }"
              @click="copyIngredients"
            >
              <svg
                v-if="copyStatus !== '✓ Copied!'"
                xmlns="http://www.w3.org/2000/svg"
                width="15"
                height="15"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
              </svg>
              <span>{{ copyStatus || 'Copy' }}</span>
            </button>
            <button
              v-if="checkedIngredients.size > 0 || completedSteps.size > 0"
              type="button"
              class="reset-btn"
              @click="resetChecklist"
            >
              Reset
            </button>
          </div>
        </div>
        <p class="section-hint">Check off ingredients as you prepare them:</p>
        
        <div class="ingredients-table-wrapper">
          <table class="ingredients-table">
            <thead>
              <tr>
                <th style="width: 40px;"></th>
                <th>Amount</th>
                <th>Unit</th>
                <th>Ingredient</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(item, idx) in convertedIngredients"
                :key="idx"
                :class="{ 'item-checked': isChecked(recipe.ingredients[idx]) }"
                @click="toggleIngredient(recipe.ingredients[idx])"
              >
                <td>
                  <input
                    type="checkbox"
                    :checked="isChecked(recipe.ingredients[idx])"
                    @click.stop="toggleIngredient(recipe.ingredients[idx])"
                  />
                </td>
                <td class="amount-cell">{{ item.amount }}</td>
                <td class="unit-cell">{{ item.unit }}</td>
                <td class="name-cell">{{ item.name }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="recipe-block">
        <div class="recipe-section-header">
          <h2>Steps</h2>
          <span v-if="completedSteps.size > 0" class="step-progress-badge">
            {{ completedSteps.size }} of {{ recipe.steps.length }} completed
          </span>
        </div>
        <p class="section-hint">Tap each step to track your cooking progress:</p>
        <ol class="step-list">
          <li
            v-for="(step, idx) in recipe.steps"
            :key="idx"
            class="step-item"
            :class="{ 'step-done': completedSteps.has(idx) }"
            @click="toggleStep(idx)"
          >
            <span class="step-number">{{ idx + 1 }}</span>
            <div class="step-content">
              <p>{{ step }}</p>
            </div>
          </li>
        </ol>
      </div>
    </article>
  </main>
</template>

<style scoped>
.unit-toggle-group {
  display: inline-flex;
  background: var(--card-bg, #1a1d26);
  border: 1px solid var(--card-border, #2a2e3d);
  border-radius: 6px;
  overflow: hidden;
  margin-right: 6px;
}
.unit-toggle-group button {
  background: transparent;
  border: none;
  padding: 4px 10px;
  font-size: 12px;
  color: var(--text-muted, #94a3b8);
  cursor: pointer;
}
.unit-toggle-group button.active {
  background: var(--primary, #aa3bff);
  color: #fff;
  font-weight: 600;
}
.ingredients-table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--card-border, #2a2e3d);
  border-radius: 8px;
  background: var(--card-bg, #1a1d26);
}
.ingredients-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 14px;
}
.ingredients-table th,
.ingredients-table td {
  padding: 10px 14px;
  border-bottom: 1px solid var(--card-border, #2a2e3d);
}
.ingredients-table th {
  font-weight: 600;
  color: var(--text-muted, #94a3b8);
  background: rgba(255, 255, 255, 0.02);
}
.ingredients-table tr:last-child td {
  border-bottom: none;
}
.ingredients-table tr {
  cursor: pointer;
  transition: background 0.15s;
}
.ingredients-table tr:hover {
  background: rgba(255, 255, 255, 0.04);
}
.ingredients-table tr.item-checked {
  opacity: 0.5;
  text-decoration: line-through;
}
.amount-cell {
  font-weight: 600;
  width: 90px;
}
.unit-cell {
  color: var(--text-muted, #94a3b8);
  width: 100px;
}
</style>

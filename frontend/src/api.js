const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

export async function fetchRecipes(query = '', filters = {}) {
  const params = new URLSearchParams()
  if (query) params.set('q', query)
  if (filters.category) params.set('category', filters.category)
  if (filters.difficulty) params.set('difficulty', filters.difficulty)
  if (filters.max_cook_time) params.set('max_cook_time', filters.max_cook_time)
  const qs = params.toString()
  const url = qs ? `${API_BASE}/api/recipes?${qs}` : `${API_BASE}/api/recipes`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Network response was not ok')
  return res.json()
}

export async function fetchRecipe(id) {
  const res = await fetch(`${API_BASE}/api/recipes/${id}`)
  if (res.status === 404) throw new Error('Recipe not found')
  if (!res.ok) throw new Error('Network response was not ok')
  return res.json()
}

export async function sendChatMessage(message, history = []) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.detail || 'Chat request failed')
  return data
}

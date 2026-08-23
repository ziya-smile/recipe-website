import { createRouter, createWebHistory } from 'vue-router'
import HomePage from './views/HomePage.vue'
import RecipesPage from './views/RecipesPage.vue'
import RecipePage from './views/RecipePage.vue'
import FavoritesPage from './views/FavoritesPage.vue'
import AuthPage from './views/AuthPage.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomePage },
    { path: '/recipes', name: 'recipes', component: RecipesPage },
    { path: '/recipes/:id', name: 'recipe', component: RecipePage },
    { path: '/favorites', name: 'favorites', component: FavoritesPage },
    { path: '/auth', name: 'auth', component: AuthPage },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

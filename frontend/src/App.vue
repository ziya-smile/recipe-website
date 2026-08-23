<script setup>
import ChatBot from './components/ChatBot.vue'
</script>

<template>
  <div class="site">
    <header class="site-header">
      <RouterLink class="logo" to="/">Fun recipes</RouterLink>
      <nav class="nav-links">
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/recipes">Recipes</RouterLink>
      </nav>
    </header>
    <RouterView />
    <ChatBot />
  </div>
</template>

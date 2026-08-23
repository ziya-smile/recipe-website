<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '../supabase'

const router = useRouter()
const isSignUp = ref(false)
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const loading = ref(false)

async function handleSubmit() {
  errorMsg.value = ''
  successMsg.value = ''
  loading.value = true

  try {
    if (isSignUp.value) {
      const { data, error } = await supabase.auth.signUp({
        email: email.value,
        password: password.value,
      })
      if (error) throw error
      successMsg.value = 'Account created successfully! You can now log in.'
      isSignUp.value = false
    } else {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.value,
        password: password.value,
      })
      if (error) throw error
      router.push('/')
    }
  } catch (err) {
    errorMsg.value = err.message || 'An error occurred during authentication.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1 class="auth-title">{{ isSignUp ? 'Create Account' : 'Welcome Back' }}</h1>
      <p class="auth-subtitle">
        {{ isSignUp ? 'Sign up to manage your recipes & favorites' : 'Log in to your account' }}
      </p>

      <div v-if="errorMsg" class="auth-error">{{ errorMsg }}</div>
      <div v-if="successMsg" class="auth-success">{{ successMsg }}</div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-group">
          <label>Email</label>
          <input type="email" v-model="email" required placeholder="you@example.com" />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="password" required placeholder="••••••••" />
        </div>

        <button type="submit" class="auth-button" :disabled="loading">
          {{ loading ? 'Processing...' : (isSignUp ? 'Sign Up' : 'Log In') }}
        </button>
      </form>

      <div class="auth-switch">
        <p>
          {{ isSignUp ? 'Already have an account?' : "Don't have an account?" }}
          <button type="button" @click="isSignUp = !isSignUp" class="switch-btn">
            {{ isSignUp ? 'Log In' : 'Sign Up' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 80px);
  padding: 2rem;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--bg-card, #fff);
  border: 1px solid var(--border-color, #eaeaea);
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.auth-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-align: center;
}

.auth-subtitle {
  color: var(--text-muted, #666);
  text-align: center;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.auth-error {
  background: #fee2e2;
  color: #991b1b;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.auth-success {
  background: #d1fae5;
  color: #065f46;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
}

.form-group input {
  padding: 0.75rem;
  border: 1px solid var(--border-color, #ccc);
  border-radius: 6px;
  font-size: 1rem;
  background: var(--input-bg, #fff);
  color: var(--text-color, #000);
}

.auth-button {
  background: var(--primary-color, #2563eb);
  color: white;
  padding: 0.75rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.auth-button:hover {
  opacity: 0.9;
}

.auth-switch {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-muted, #666);
}

.switch-btn {
  background: none;
  border: none;
  color: var(--primary-color, #2563eb);
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  margin-left: 0.25rem;
}
</style>

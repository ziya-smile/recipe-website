<script setup>
import { ref, nextTick, watch } from 'vue'
import { sendChatMessage } from '../api'

const open = ref(false)
const input = ref('')
const loading = ref(false)
const messages = ref([
  {
    role: 'assistant',
    content: "Hi! I'm your recipe assistant 🍳 Ask me to recommend a dish, help with substitutions, or give cooking tips!",
  },
])
const messagesEl = ref(null)

function scrollToBottom() {
  nextTick(() => {
    if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  })
}

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  scrollToBottom()
  loading.value = true

  const history = messages.value
    .slice(1, -1)
    .map((m) => ({ role: m.role === 'assistant' ? 'model' : 'user', content: m.content }))

  try {
    const data = await sendChatMessage(text, history)
    messages.value.push({ role: 'assistant', content: data.reply })
  } catch (err) {
    messages.value.push({ role: 'error', content: err.message })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

watch(open, (val) => {
  if (val) scrollToBottom()
})
</script>

<template>
  <div>
    <button
      class="chat-toggle"
      :aria-label="open ? 'Close chat' : 'Open chat assistant'"
      @click="open = !open"
    >
      <svg v-if="!open" xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M18 6 6 18M6 6l12 12" />
      </svg>
    </button>

    <div v-if="open" class="chat-panel">
      <div class="chat-header">
        <div class="chat-header-title">
          <span>🍳</span>
          <span>Recipe Assistant</span>
        </div>
        <button class="chat-close" aria-label="Close chat" @click="open = false">✕</button>
      </div>

      <div ref="messagesEl" class="chat-messages">
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="chat-msg"
          :class="msg.role"
        >
          {{ msg.content }}
        </div>
        <div v-if="loading" class="chat-typing">
          <span></span><span></span><span></span>
        </div>
      </div>

      <div class="chat-input-row">
        <input
          v-model="input"
          class="chat-input"
          placeholder="Ask about recipes or cooking..."
          :disabled="loading"
          @keydown.enter="send"
        />
        <button class="chat-send" :disabled="loading || !input.trim()" @click="send" aria-label="Send message">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="m22 2-7 20-4-9-9-4Z" />
            <path d="M22 2 11 13" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

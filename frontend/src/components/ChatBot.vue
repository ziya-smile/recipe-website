<script setup>
import { ref, nextTick, onMounted } from 'vue'

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

const isOpen = ref(false)
const messages = ref([
  { role: 'assistant', content: "Hi! I'm your cooking assistant 👨‍🍳 Ask me anything about recipes, cooking tips, or substitutions!" }
])
const input = ref('')
const isLoading = ref(false)
const messagesEl = ref(null)
const inputEl = ref(null)
const error = ref('')

function toggleChat() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    nextTick(() => {
      inputEl.value?.focus()
      scrollToBottom()
    })
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  })
}

async function sendMessage() {
  const text = input.value.trim()
  if (!text || isLoading.value) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  error.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: messages.value }),
    })

    if (!res.ok) throw new Error(`Server error: ${res.status}`)

    const data = await res.json()
    messages.value.push({ role: 'assistant', content: data.reply })
  } catch (err) {
    error.value = 'Something went wrong. Please try again.'
    messages.value.pop() // remove the user message that failed
    input.value = text   // restore input
  } finally {
    isLoading.value = false
    scrollToBottom()
    nextTick(() => inputEl.value?.focus())
  }
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}
</script>

<template>
  <!-- Floating button -->
  <div class="chatbot-root" role="complementary" aria-label="AI cooking assistant">
    <button
      class="chatbot-fab"
      :aria-expanded="isOpen"
      aria-controls="chatbot-panel"
      aria-label="Open cooking assistant"
      @click="toggleChat"
    >
      <svg v-if="!isOpen" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>

    <!-- Chat panel -->
    <div
      v-if="isOpen"
      id="chatbot-panel"
      class="chatbot-panel"
      role="dialog"
      aria-label="AI cooking assistant"
      aria-modal="false"
    >
      <div class="chatbot-header">
        <div class="chatbot-header-info">
          <div class="chatbot-avatar" aria-hidden="true">🍳</div>
          <div>
            <div class="chatbot-title">Cooking Assistant</div>
            <div class="chatbot-subtitle">Powered by Gemini AI</div>
          </div>
        </div>
        <button class="chatbot-close-btn" aria-label="Close chat" @click="toggleChat">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <div ref="messagesEl" class="chatbot-messages" aria-live="polite" aria-label="Conversation">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="chatbot-msg"
          :class="msg.role === 'user' ? 'chatbot-msg--user' : 'chatbot-msg--assistant'"
        >
          <div class="chatbot-bubble">{{ msg.content }}</div>
        </div>
        <div v-if="isLoading" class="chatbot-msg chatbot-msg--assistant" aria-label="Assistant is typing">
          <div class="chatbot-bubble chatbot-typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div v-if="error" class="chatbot-error" role="alert">{{ error }}</div>

      <div class="chatbot-input-row">
        <textarea
          ref="inputEl"
          v-model="input"
          class="chatbot-input"
          placeholder="Ask about a recipe…"
          rows="1"
          :disabled="isLoading"
          aria-label="Message the cooking assistant"
          @keydown="handleKeydown"
        ></textarea>
        <button
          class="chatbot-send-btn"
          :disabled="!input.trim() || isLoading"
          aria-label="Send message"
          @click="sendMessage"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chatbot-root {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.chatbot-fab {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  transition: transform 0.2s, box-shadow 0.2s;
  flex-shrink: 0;
}

.chatbot-fab:hover {
  transform: scale(1.07);
  box-shadow: 0 6px 24px rgba(0,0,0,0.28);
}

.chatbot-panel {
  width: 360px;
  max-width: calc(100vw - 48px);
  height: 480px;
  max-height: calc(100svh - 120px);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.18);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chatbot-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--muted-bg);
  flex-shrink: 0;
}

.chatbot-header-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chatbot-avatar {
  font-size: 28px;
  line-height: 1;
}

.chatbot-title {
  font-weight: 600;
  color: var(--text-h);
  font-size: 15px;
}

.chatbot-subtitle {
  font-size: 12px;
  color: var(--text);
  opacity: 0.8;
}

.chatbot-close-btn {
  background: none;
  border: none;
  color: var(--text);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  border-radius: 6px;
  transition: background-color 0.15s;
}

.chatbot-close-btn:hover {
  background: var(--border);
  color: var(--text-h);
}

.chatbot-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  scroll-behavior: smooth;
}

.chatbot-msg {
  display: flex;
}

.chatbot-msg--user {
  justify-content: flex-end;
}

.chatbot-msg--assistant {
  justify-content: flex-start;
}

.chatbot-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.chatbot-msg--user .chatbot-bubble {
  background: var(--accent);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.chatbot-msg--assistant .chatbot-bubble {
  background: var(--muted-bg);
  color: var(--text-h);
  border: 1px solid var(--border);
  border-bottom-left-radius: 4px;
}

.chatbot-typing {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
}

.chatbot-typing span {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text);
  opacity: 0.4;
  animation: chatbot-bounce 1.2s infinite;
}

.chatbot-typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.chatbot-typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes chatbot-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

.chatbot-error {
  padding: 8px 16px;
  background: #fee2e2;
  color: #991b1b;
  font-size: 13px;
  text-align: center;
  flex-shrink: 0;
}

.chatbot-input-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 12px 14px;
  border-top: 1px solid var(--border);
  background: var(--muted-bg);
  flex-shrink: 0;
}

.chatbot-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--bg);
  color: var(--text-h);
  font-family: inherit;
  font-size: 14px;
  resize: none;
  outline: none;
  line-height: 1.4;
  max-height: 80px;
  overflow-y: auto;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.chatbot-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-bg);
}

.chatbot-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.chatbot-send-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: var(--accent);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: filter 0.15s, transform 0.15s;
}

.chatbot-send-btn:hover:not(:disabled) {
  filter: brightness(1.1);
  transform: scale(1.05);
}

.chatbot-send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .chatbot-root {
    bottom: 16px;
    right: 16px;
  }
  .chatbot-panel {
    width: calc(100vw - 32px);
    max-width: 100%;
    height: 420px;
  }
}
</style>

<script setup lang="ts">
import { ref, nextTick, onMounted, watch } from 'vue'
import { chat, chatStream } from '../api'
import { marked } from 'marked'
import KnowledgeBaseSelector from './KnowledgeBaseSelector.vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: any[]
  streaming?: boolean
  error?: boolean
  time?: string
}

const messages = ref<Message[]>([])
const inputQuery = ref('')
const collectionName = ref('default')
const useStream = ref(true)
const loading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const textarea = ref<HTMLTextAreaElement | null>(null)

onMounted(() => {
  messages.value.push({
    role: 'assistant',
    content: '你好！我是 RAG 文档问答助手。\n\n请先在右上角选择一个知识库，然后输入问题进行提问。',
    time: formatTime(),
  })
  autoResize()
})

function formatTime() {
  const d = new Date()
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function autoResize() {
  if (textarea.value) {
    textarea.value.style.height = 'auto'
    textarea.value.style.height = Math.min(textarea.value.scrollHeight, 120) + 'px'
  }
}

watch(inputQuery, () => {
  nextTick(autoResize)
})

let abortController: AbortController | null = null

async function sendMessage() {
  const query = inputQuery.value.trim()
  if (!query || loading.value) return

  if (!collectionName.value) {
    alert('请先选择知识库')
    return
  }

  messages.value.push({ role: 'user', content: query, time: formatTime() })
  inputQuery.value = ''
  loading.value = true

  const assistantMsg: Message = {
    role: 'assistant',
    content: '',
    streaming: true,
    time: formatTime(),
  }
  messages.value.push(assistantMsg)

  await scrollToBottom()

  try {
    if (useStream.value) {
      abortController = new AbortController()
      const stream = await chatStream(query, collectionName.value)
      const reader = stream.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        assistantMsg.content += decoder.decode(value, { stream: true })
        await scrollToBottom()
      }
    } else {
      const result = await chat(query, collectionName.value)
      assistantMsg.content = result.answer
      assistantMsg.sources = result.sources
    }
  } catch (e: any) {
    assistantMsg.error = true
    assistantMsg.content = `请求失败: ${e.message || '未知错误'}`
  } finally {
    assistantMsg.streaming = false
    loading.value = false
    abortController = null
    await scrollToBottom()
  }
}

function stopGeneration() {
  if (abortController) {
    abortController.abort()
    abortController = null
  }
  loading.value = false
  const last = messages.value[messages.value.length - 1]
  if (last && last.streaming) {
    last.streaming = false
    if (!last.content) {
      last.content = '(已停止)'
    }
  }
}

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function renderMarkdown(content: string): string {
  try {
    return marked(content) as string
  } catch {
    return content
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

function clearMessages() {
  messages.value = [{
    role: 'assistant',
    content: '对话已清空，请输入新问题。',
    time: formatTime(),
  }]
}

const quickQuestions = ['总结文档内容', '主要技术栈是什么？', '有哪些核心功能？']
</script>

<template>
  <div class="chat-panel">
    <!-- 顶部配置栏 -->
    <div class="chat-header">
      <div class="header-left">
        <div class="header-title">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
          </svg>
          <span>智能问答</span>
        </div>
      </div>
      <div class="header-right">
        <KnowledgeBaseSelector v-model="collectionName" />
        <label class="stream-toggle" title="流式输出">
          <input type="checkbox" v-model="useStream" />
          <span class="toggle-track"><span class="toggle-thumb"></span></span>
          <span class="toggle-label">流式</span>
        </label>
        <button class="icon-btn" title="清空对话" @click="clearMessages">
          <svg viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 消息列表 -->
    <div ref="messagesContainer" class="messages">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="message-row"
        :class="msg.role"
      >
        <div class="avatar">
          <svg v-if="msg.role === 'assistant'" viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M12 2A2 2 0 0 1 14 4C14 4.74 13.6 5.39 13 5.73V7H14A7 7 0 0 1 21 14H22A1 1 0 0 1 23 15V18A1 1 0 0 1 22 19H21V20A2 2 0 0 1 19 22H5A2 2 0 0 1 3 20V19H2A1 1 0 0 1 1 18V15A1 1 0 0 1 2 14H3A7 7 0 0 1 10 7H11V5.73C10.4 5.39 10 4.74 10 4A2 2 0 0 1 12 2M7.5 13A2.5 2.5 0 0 0 5 15.5A2.5 2.5 0 0 0 7.5 18A2.5 2.5 0 0 0 10 15.5A2.5 2.5 0 0 0 7.5 13M16.5 13A2.5 2.5 0 0 0 14 15.5A2.5 2.5 0 0 0 16.5 18A2.5 2.5 0 0 0 19 15.5A2.5 2.5 0 0 0 16.5 13Z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M12 4A4 4 0 0 1 16 8A4 4 0 0 1 12 12A4 4 0 0 1 8 8A4 4 0 0 1 12 4M12 14C16.42 14 20 15.79 20 18V20H4V18C4 15.79 7.58 14 12 14Z"/>
          </svg>
        </div>
        <div class="bubble-wrap">
          <div class="bubble" :class="{ error: msg.error }">
            <!-- 打字指示器 -->
            <div v-if="msg.streaming && !msg.content" class="typing-indicator">
              <span></span><span></span><span></span>
            </div>

            <div v-else-if="msg.role === 'assistant'" class="content" v-html="renderMarkdown(msg.content)"></div>
            <div v-else class="content">{{ msg.content }}</div>

            <span v-if="msg.streaming && msg.content" class="cursor"></span>

            <!-- 来源引用 -->
            <div v-if="msg.sources && msg.sources.length" class="sources">
              <div class="sources-title">
                <svg viewBox="0 0 24 24" width="12" height="12">
                  <path fill="currentColor" d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81a3 3 0 0 0 3-3 3 3 0 0 0-3-3 3 3 0 0 0-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9a3 3 0 0 0-3 3 3 3 0 0 0 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65a3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3z"/>
                </svg>
                参考来源
              </div>
              <div v-for="(src, idx) in msg.sources" :key="idx" class="source-item">
                <span class="source-score">{{ (src.score * 100).toFixed(1) }}%</span>
                <span class="source-content">{{ src.content }}</span>
              </div>
            </div>
          </div>
          <div v-if="msg.time" class="msg-time">{{ msg.time }}</div>
        </div>
      </div>
    </div>

    <!-- 快捷问题 -->
    <div v-if="messages.length <= 1" class="quick-questions">
      <div class="quick-title">试试这些问题：</div>
      <div class="quick-list">
        <button v-for="q in quickQuestions" :key="q" @click="inputQuery = q; sendMessage()">
          <svg viewBox="0 0 24 24" width="12" height="12">
            <path fill="currentColor" d="M9 5l7 7-7 7"/>
          </svg>
          {{ q }}
        </button>
      </div>
    </div>

    <!-- 输入区 -->
    <div class="input-area">
      <div class="input-wrapper">
        <textarea
          ref="textarea"
          v-model="inputQuery"
          placeholder="输入问题，Enter 发送，Shift+Enter 换行..."
          @keydown="handleKeydown"
          rows="1"
          :disabled="loading"
        ></textarea>
        <button v-if="!loading" @click="sendMessage" :disabled="!inputQuery.trim()" class="send-btn" title="发送">
          <svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg>
        </button>
        <button v-else @click="stopGeneration" class="stop-btn" title="停止">
          <svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M6 6h12v12H6z"/></svg>
        </button>
      </div>
      <div class="input-hint">
        <span>当前知识库：<b>{{ collectionName || '未选择' }}</b></span>
        <span v-if="loading">生成中...</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(180deg, #fafbff 0%, #f5f7fb 100%);
}

/* 头部 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 24px;
  background: white;
  border-bottom: 1px solid #eee;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  z-index: 2;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.header-title svg {
  color: #6366f1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 流式开关 */
.stream-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 12px;
  color: #6b7280;
  user-select: none;
}

.stream-toggle input {
  display: none;
}

.toggle-track {
  width: 32px;
  height: 18px;
  background: #d1d5db;
  border-radius: 9px;
  position: relative;
  transition: background 0.2s;
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 14px;
  height: 14px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.stream-toggle input:checked + .toggle-track {
  background: #6366f1;
}

.stream-toggle input:checked + .toggle-track .toggle-thumb {
  transform: translateX(14px);
}

.icon-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #9ca3af;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: #f3f4f6;
  color: #ef4444;
}

/* 消息区 */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
}

.message-row {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.message-row.user .avatar {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.bubble-wrap {
  display: flex;
  flex-direction: column;
  max-width: 75%;
}

.message-row.user .bubble-wrap {
  align-items: flex-end;
}

.bubble {
  padding: 12px 16px;
  border-radius: 14px;
  line-height: 1.65;
  font-size: 14px;
  position: relative;
}

.bubble.error {
  background: #fef2f2 !important;
  color: #dc2626 !important;
  border: 1px solid #fecaca;
}

.message-row.assistant .bubble {
  background: white;
  color: #1f2937;
  border: 1px solid #e5e7eb;
  border-top-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.message-row.user .bubble {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: white;
  border-top-right-radius: 4px;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
}

.msg-time {
  font-size: 10px;
  color: #9ca3af;
  margin-top: 4px;
  padding: 0 4px;
}

.content :deep(p) {
  margin: 6px 0;
}

.content :deep(p:first-child) {
  margin-top: 0;
}

.content :deep(p:last-child) {
  margin-bottom: 0;
}

.content :deep(code) {
  background: rgba(99, 102, 241, 0.1);
  color: #4f46e5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'Consolas', 'Monaco', monospace;
}

.content :deep(pre) {
  background: #1f2937;
  color: #e5e7eb;
  padding: 12px 14px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
  font-size: 13px;
}

.content :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
}

.content :deep(ul),
.content :deep(ol) {
  padding-left: 20px;
  margin: 6px 0;
}

.content :deep(table) {
  border-collapse: collapse;
  margin: 8px 0;
  width: 100%;
}

.content :deep(th),
.content :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 6px 10px;
  font-size: 13px;
}

.content :deep(th) {
  background: #f9fafb;
  font-weight: 600;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 6px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c7d2fe;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* 流式光标 */
.cursor {
  display: inline-block;
  width: 2px;
  height: 16px;
  background: #6366f1;
  margin-left: 2px;
  vertical-align: text-bottom;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 来源引用 */
.sources {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px dashed #e5e7eb;
}

.sources-title {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 6px;
  font-weight: 500;
}

.source-item {
  display: flex;
  gap: 8px;
  font-size: 12px;
  margin-bottom: 4px;
  padding: 6px 8px;
  background: #f9fafb;
  border-radius: 6px;
  border-left: 2px solid #6366f1;
}

.source-score {
  color: #6366f1;
  font-weight: 600;
  flex-shrink: 0;
}

.source-content {
  color: #6b7280;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 快捷问题 */
.quick-questions {
  padding: 0 24px 12px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.quick-title {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 8px;
}

.quick-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-list button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #e5e7eb;
  background: white;
  color: #4f46e5;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-list button:hover {
  background: #eef2ff;
  border-color: #c7d2fe;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(99, 102, 241, 0.1);
}

.quick-list button svg {
  color: #9ca3af;
}

/* 输入区 */
.input-area {
  padding: 12px 24px 16px;
  background: white;
  border-top: 1px solid #eee;
}

.input-wrapper {
  display: flex;
  gap: 8px;
  align-items: flex-end;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 6px 6px 6px 14px;
  transition: all 0.2s;
  max-width: 900px;
  margin: 0 auto;
}

.input-wrapper:focus-within {
  border-color: #6366f1;
  background: white;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.input-wrapper textarea {
  flex: 1;
  padding: 8px 0;
  border: none;
  background: transparent;
  font-size: 14px;
  resize: none;
  font-family: inherit;
  box-sizing: border-box;
  line-height: 1.5;
  max-height: 120px;
  outline: none;
  color: #1f2937;
}

.input-wrapper textarea::placeholder {
  color: #9ca3af;
}

.send-btn, .stop-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: white;
  box-shadow: 0 2px 6px rgba(99, 102, 241, 0.3);
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.send-btn:disabled {
  background: #d1d5db;
  box-shadow: none;
  cursor: not-allowed;
}

.stop-btn {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.3);
}

.stop-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.input-hint {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #9ca3af;
  margin-top: 8px;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
  padding: 0 4px;
}

.input-hint b {
  color: #6366f1;
}

/* 滚动条 */
.messages::-webkit-scrollbar {
  width: 6px;
}

.messages::-webkit-scrollbar-track {
  background: transparent;
}

.messages::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { listCollections } from '../api'

interface Collection {
  name: string
  count: number
}

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'refresh'): void
}>()

const collections = ref<Collection[]>([])
const open = ref(false)
const loading = ref(false)
const searchText = ref('')
const dropdownRef = ref<HTMLElement | null>(null)

const filtered = computed(() => {
  if (!searchText.value) return collections.value
  const q = searchText.value.toLowerCase()
  return collections.value.filter(c => c.name.toLowerCase().includes(q))
})

async function loadCollections() {
  loading.value = true
  try {
    const data = await listCollections()
    collections.value = data.collections || []
  } catch (e) {
    console.error('加载知识库列表失败', e)
  } finally {
    loading.value = false
  }
}

function toggle() {
  open.value = !open.value
  if (open.value) {
    searchText.value = ''
    loadCollections()
  }
}

function select(name: string) {
  emit('update:modelValue', name)
  open.value = false
}

function handleClickOutside(e: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    open.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  // 初次加载一次，方便显示当前项的文档数
  loadCollections()
})

defineExpose({ refresh: loadCollections })
</script>

<template>
  <div class="kb-selector" ref="dropdownRef">
    <div class="selector-trigger" @click="toggle" :class="{ active: open }">
      <svg class="icon-db" viewBox="0 0 24 24" width="16" height="16">
        <path fill="currentColor" d="M12 3C7.58 3 4 4.79 4 7s3.58 4 8 4 8-1.79 8-4-3.58-4-8-4m0 6c-3.87 0-7-1.34-7-3 0-.31.13-.61.36-.89C6.36 6.04 9.04 7 12 7s5.64-.96 6.64-1.89c.23.28.36.58.36.89 0 1.66-3.13 3-7 3m0 4c-4.42 0-8-1.79-8-4v3c0 2.21 3.58 4 8 4s8-1.79 8-4v-3c0 2.21-3.58 4-8 4m0 4c-4.42 0-8-1.79-8-4v3c0 2.21 3.58 4 8 4s8-1.79 8-4v-3c0 2.21-3.58 4-8 4z"/>
      </svg>
      <div class="trigger-info">
        <div class="trigger-name">{{ modelValue || '选择知识库' }}</div>
        <div class="trigger-meta">
          <span v-if="loading">加载中...</span>
          <span v-else-if="collections.find(c => c.name === modelValue)">
            {{ collections.find(c => c.name === modelValue)?.count }} 个文档块
          </span>
          <span v-else>未找到</span>
        </div>
      </div>
      <svg class="icon-arrow" :class="{ rotated: open }" viewBox="0 0 24 24" width="14" height="14">
        <path fill="currentColor" d="M7 10l5 5 5-5z"/>
      </svg>
    </div>

    <transition name="dropdown">
      <div v-if="open" class="dropdown-panel">
        <div class="search-box">
          <svg viewBox="0 0 24 24" width="14" height="14">
            <path fill="currentColor" d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 0 0 1.48-5.34c-.47-2.78-2.79-5-5.59-5.34a6.505 6.505 0 0 0-7.27 7.27c.34 2.8 2.56 5.12 5.34 5.59a6.5 6.5 0 0 0 5.34-1.48l.27.28v.79l4.25 4.25c.41.41 1.08.41 1.49 0 .41-.41.41-1.08 0-1.49L15.5 14zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
          </svg>
          <input v-model="searchText" placeholder="搜索或新建..." @click.stop />
          <button class="new-btn" @click.stop="select(searchText.trim())" :disabled="!searchText.trim()">
            + 新建
          </button>
        </div>

        <div class="options">
          <div v-if="loading" class="empty">加载中...</div>
          <div v-else-if="filtered.length === 0" class="empty">
            {{ collections.length === 0 ? '暂无知识库，输入名称新建' : '无匹配结果' }}
          </div>
          <div
            v-for="col in filtered"
            :key="col.name"
            class="option"
            :class="{ selected: col.name === modelValue }"
            @click="select(col.name)"
          >
            <div class="option-icon">
              <svg viewBox="0 0 24 24" width="18" height="18">
                <path fill="currentColor" d="M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zm0 2v12h16V6H4zm2 2h12v2H6V8zm0 4h8v2H6v-2zm0 4h4v2H6v-2z"/>
              </svg>
            </div>
            <div class="option-content">
              <div class="option-name">{{ col.name }}</div>
              <div class="option-meta">{{ col.count }} 个文档块</div>
            </div>
            <span v-if="col.name === modelValue" class="check">
              <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            </span>
          </div>
        </div>

        <div class="dropdown-footer" @click="loadCollections">
          <svg viewBox="0 0 24 24" width="12" height="12" style="margin-right:4px">
            <path fill="currentColor" d="M17.65 6.35A7.958 7.958 0 0 0 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0 1 12 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
          </svg>
          刷新列表
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.kb-selector {
  position: relative;
  width: 220px;
}

.selector-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  height: 40px;
  box-sizing: border-box;
}

.selector-trigger:hover {
  border-color: #c7d2fe;
  background: #fafbff;
}

.selector-trigger.active {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.icon-db {
  color: #6366f1;
  flex-shrink: 0;
}

.trigger-info {
  flex: 1;
  min-width: 0;
  text-align: left;
}

.trigger-name {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.trigger-meta {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 2px;
}

.icon-arrow {
  color: #9ca3af;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.icon-arrow.rotated {
  transform: rotate(180deg);
}

.dropdown-panel {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08), 0 4px 6px rgba(0, 0, 0, 0.05);
  z-index: 100;
  overflow: hidden;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border-bottom: 1px solid #f3f4f6;
  background: #fafafa;
}

.search-box svg {
  color: #9ca3af;
}

.search-box input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 13px;
  background: transparent;
  padding: 4px 0;
}

.new-btn {
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.new-btn:hover:not(:disabled) {
  background: #4f46e5;
}

.new-btn:disabled {
  background: #c7d2fe;
  cursor: not-allowed;
}

.options {
  max-height: 260px;
  overflow-y: auto;
  padding: 4px;
}

.empty {
  padding: 24px 12px;
  text-align: center;
  color: #9ca3af;
  font-size: 13px;
}

.option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.option:hover {
  background: #f5f3ff;
}

.option.selected {
  background: #eef2ff;
}

.option-icon {
  color: #6366f1;
  flex-shrink: 0;
  display: flex;
}

.option-content {
  flex: 1;
  min-width: 0;
}

.option-name {
  font-size: 13px;
  color: #1f2937;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.option-meta {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 2px;
}

.check {
  color: #6366f1;
  flex-shrink: 0;
}

.dropdown-footer {
  padding: 8px 12px;
  border-top: 1px solid #f3f4f6;
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.dropdown-footer:hover {
  background: #f9fafb;
  color: #6366f1;
}

/* 下拉动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>

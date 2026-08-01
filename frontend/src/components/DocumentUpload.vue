<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { uploadDocument, getSupportedFormats } from '../api'

const supportedFormats = ref<string[]>([])
const collectionName = ref('default')
const uploading = ref(false)
const uploadResult = ref<any>(null)
const dragOver = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

onMounted(async () => {
  try {
    const data = await getSupportedFormats()
    supportedFormats.value = data.formats || []
  } catch (e) {
    console.error('获取支持格式失败', e)
  }
})

function handleFileSelect() {
  fileInput.value?.click()
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    doUpload(target.files[0])
  }
}

function handleDrop(event: DragEvent) {
  dragOver.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    doUpload(event.dataTransfer.files[0])
  }
}

function handleDragOver() {
  dragOver.value = true
}

function handleDragLeave() {
  dragOver.value = false
}

async function doUpload(file: File) {
  uploading.value = true
  uploadResult.value = null
  try {
    const result = await uploadDocument(file, collectionName.value)
    uploadResult.value = { type: 'success', data: result }
  } catch (e: any) {
    uploadResult.value = {
      type: 'error',
      message: e.response?.data?.detail || e.message || '上传失败',
    }
  } finally {
    uploading.value = false
  }
}

</script>

<template>
  <div class="upload-panel">
    <h3>文档上传</h3>

    <!-- 集合名称 -->
    <div class="form-group">
      <label>知识库名称</label>
      <input v-model="collectionName" type="text" placeholder="输入知识库名称" />
    </div>

    <!-- 拖拽上传区域 -->
    <div
      class="drop-zone"
      :class="{ active: dragOver, uploading }"
      @click="handleFileSelect"
      @drop.prevent="handleDrop"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
    >
      <input
        ref="fileInput"
        type="file"
        style="display: none"
        :accept="supportedFormats.join(',')"
        @change="handleFileChange"
      />
      <div v-if="!uploading" class="drop-content">
        <svg class="upload-icon" viewBox="0 0 24 24" width="48" height="48">
          <path
            fill="currentColor"
            d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"
          />
        </svg>
        <p>点击或拖拽文件到此处上传</p>
        <p class="hint">支持: {{ supportedFormats.join(', ') }}</p>
      </div>
      <div v-else class="loading-content">
        <div class="spinner"></div>
        <p>正在上传并解析...</p>
      </div>
    </div>

    <!-- 上传结果 -->
    <div v-if="uploadResult" class="result" :class="uploadResult.type">
      <div v-if="uploadResult.type === 'success'" class="success-result">
        <p>上传成功</p>
        <p>文件名: {{ uploadResult.data.filename }}</p>
        <p>已存储: {{ uploadResult.data.stored ? '是' : '否' }}</p>
        <p>文档数: {{ uploadResult.data.doc_count }}</p>
        <p v-if="uploadResult.data.duplicate" class="warn">注意: 文件已存在，跳过重复处理</p>
      </div>
      <div v-else class="error-result">
        <p>上传失败: {{ uploadResult.message }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-panel {
  padding: 20px;
}

h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #666;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.drop-zone {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.drop-zone:hover,
.drop-zone.active {
  border-color: #4f46e5;
  background: #f5f3ff;
}

.drop-zone.uploading {
  pointer-events: none;
  opacity: 0.7;
}

.drop-content {
  color: #666;
}

.upload-icon {
  color: #999;
  margin-bottom: 8px;
}

.drop-content p {
  margin: 4px 0;
}

.drop-content .hint {
  font-size: 12px;
  color: #aaa;
}

.loading-content {
  color: #666;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 8px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.result {
  margin-top: 16px;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
}

.result.success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.result.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
}

.success-result p,
.error-result p {
  margin: 4px 0;
}

.warn {
  color: #d97706;
}
</style>

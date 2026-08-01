import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

// 文档上传
export async function uploadDocument(file: File, collectionName?: string) {
  const formData = new FormData()
  formData.append('file', file)
  if (collectionName) {
    formData.append('collection_name', collectionName)
  }
  const response = await api.post('/document/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

// 获取支持的格式
export async function getSupportedFormats() {
  const response = await api.get('/document/supported-formats')
  return response.data
}

// 获取所有知识库列表
export async function listCollections() {
  const response = await api.get('/document/collections')
  return response.data as { collections: { name: string; count: number }[]; total: number }
}

// 删除知识库
export async function deleteCollection(name: string) {
  const response = await api.delete(`/document/collections/${encodeURIComponent(name)}`)
  return response.data
}

// 健康检查
export async function healthCheck() {
  const response = await api.get('/health')
  return response.data
}

// RAG对话（非流式）
export async function chat(query: string, collectionName: string, model?: string) {
  const response = await api.post('/chat/', {
    query,
    collection_name: collectionName,
    model,
  })
  return response.data
}

// RAG对话（流式）
export async function chatStream(
  query: string,
  collectionName: string,
  model?: string
): Promise<ReadableStream<Uint8Array>> {
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, collection_name: collectionName, model }),
  })
  if (!response.body) {
    throw new Error('流式响应不可用')
  }
  return response.body
}

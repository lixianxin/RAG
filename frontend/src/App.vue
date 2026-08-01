<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DocumentUpload from './components/DocumentUpload.vue'
import ChatInterface from './components/ChatInterface.vue'
import { healthCheck } from './api'

const activeTab = ref<'upload' | 'chat'>('chat')
const backendStatus = ref<'checking' | 'online' | 'offline'>('checking')

onMounted(async () => {
  try {
    await healthCheck()
    backendStatus.value = 'online'
  } catch {
    backendStatus.value = 'offline'
  }
})
</script>

<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <!-- 装饰光斑 -->
      <div class="glow glow-1"></div>
      <div class="glow glow-2"></div>

      <div class="sidebar-content">
        <!-- Logo -->
        <div class="logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" width="22" height="22">
              <path fill="currentColor" d="M12 2A10 10 0 0 0 2 12A10 10 0 0 0 12 22A10 10 0 0 0 22 12A10 10 0 0 0 12 2M12 4A8 8 0 0 1 20 12A8 8 0 0 1 12 20A8 8 0 0 1 4 12A8 8 0 0 1 12 4M12 6A6 6 0 0 0 6 12A6 6 0 0 0 12 18A6 6 0 0 0 18 12A6 6 0 0 0 12 6M12 8A4 4 0 0 1 16 12A4 4 0 0 1 12 16A4 4 0 0 1 8 12A4 4 0 0 1 12 8Z"/>
            </svg>
          </div>
          <div class="logo-text">
            <h2>RAG 系统</h2>
            <p>智能文档问答</p>
          </div>
        </div>

        <!-- 后端状态 -->
        <div class="status-badge" :class="backendStatus">
          <span class="dot"></span>
          <span>{{ backendStatus === 'online' ? '后端已连接' : backendStatus === 'offline' ? '后端未连接' : '检查中...' }}</span>
        </div>

        <!-- 导航 -->
        <nav class="nav">
          <div class="nav-title">功能</div>
          <button :class="{ active: activeTab === 'chat' }" @click="activeTab = 'chat'">
            <svg viewBox="0 0 24 24" width="18" height="18">
              <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z" />
            </svg>
            <span>智能问答</span>
          </button>
          <button :class="{ active: activeTab === 'upload' }" @click="activeTab = 'upload'">
            <svg viewBox="0 0 24 24" width="18" height="18">
              <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
            </svg>
            <span>文档管理</span>
          </button>
        </nav>

        <div class="sidebar-footer">
          <div class="footer-card">
            <div class="footer-icon">
              <svg viewBox="0 0 24 24" width="14" height="14">
                <path fill="currentColor" d="M11 9h2V7h-2m1 13c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8m0-18A10 10 0 0 0 2 12a10 10 0 0 0 10 10a10 10 0 0 0 10-10A10 10 0 0 0 12 2m-1 15h2v-6h-2v6z"/>
              </svg>
            </div>
            <div class="footer-text">
              <div class="ft-title">提示</div>
              <div class="ft-desc">先上传文档到知识库，再使用问答</div>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <DocumentUpload v-if="activeTab === 'upload'" />
      <ChatInterface v-else />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #1a1530 0%, #251c3d 100%);
  color: white;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15);
}

/* 装饰光斑 */
.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
  pointer-events: none;
}

.glow-1 {
  width: 200px;
  height: 200px;
  background: #6366f1;
  top: -50px;
  left: -50px;
}

.glow-2 {
  width: 220px;
  height: 220px;
  background: #8b5cf6;
  bottom: -60px;
  right: -60px;
}

.sidebar-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  padding: 24px 0;
  height: 100%;
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 24px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.logo-text h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #a5b4fc, #c4b5fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.logo-text p {
  margin: 2px 0 0;
  font-size: 11px;
  color: #9ca3af;
}

/* 状态徽章 */
.status-badge {
  margin: 20px 24px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(10px);
}

.status-badge.online {
  background: rgba(34, 197, 94, 0.12);
  color: #4ade80;
  border: 1px solid rgba(74, 222, 128, 0.2);
}

.status-badge.offline {
  background: rgba(239, 68, 68, 0.12);
  color: #f87171;
  border: 1px solid rgba(248, 113, 113, 0.2);
}

.status-badge.checking {
  background: rgba(234, 179, 8, 0.12);
  color: #facc15;
  border: 1px solid rgba(250, 204, 21, 0.2);
}

.status-badge .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 8px currentColor;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 导航 */
.nav {
  flex: 1;
  padding: 8px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-title {
  font-size: 10px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 12px 12px 6px;
  font-weight: 600;
}

.nav button {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  border: none;
  background: transparent;
  color: #9ca3af;
  font-size: 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  position: relative;
  font-family: inherit;
}

.nav button:hover {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.nav button.active {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(139, 92, 246, 0.15));
  color: #c7d2fe;
  box-shadow: inset 0 0 0 1px rgba(99, 102, 241, 0.3);
}

.nav button.active::before {
  content: '';
  position: absolute;
  left: -16px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: linear-gradient(180deg, #818cf8, #c4b5fd);
  border-radius: 0 3px 3px 0;
}

/* 底部 */
.sidebar-footer {
  padding: 16px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.footer-card {
  display: flex;
  gap: 10px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
}

.footer-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a5b4fc;
  flex-shrink: 0;
}

.footer-text {
  flex: 1;
}

.ft-title {
  font-size: 12px;
  color: #e5e7eb;
  font-weight: 600;
  margin-bottom: 2px;
}

.ft-desc {
  font-size: 11px;
  color: #9ca3af;
  line-height: 1.4;
}

/* 主内容 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f5f7fb;
}
</style>

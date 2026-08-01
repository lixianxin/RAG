# Vue 3 开发实战指南

## 1. Vue 3 简介

Vue 3 是渐进式 JavaScript 框架，2020 年 9 月正式发布。相比 Vue 2，性能更好、体积更小、TypeScript 支持更完善。

### 1.1 核心特性

- **Composition API**：逻辑组合复用更灵活
- **更好的 TypeScript 支持**：完全用 TS 重写
- **更小的体积**：Tree-shaking 友好
- **更快的渲染**：编译优化、静态提升
- **Teleport/Suspense**：新内置组件
- **多根节点**：Fragment 支持

### 1.2 与 Vue 2 对比

| 特性 | Vue 2 | Vue 3 |
|------|-------|-------|
| API 风格 | Options API | Options + Composition |
| 响应式 | Object.defineProperty | Proxy |
| 生命周期 | beforeCreate 等 | setup + onMounted 等 |
| 根节点 | 单根 | 多根（Fragment） |
| TypeScript | 支持有限 | 原生支持 |
| 体积 | 较大 | 更小 |

## 2. 创建项目

### 2.1 使用 Vite（推荐）

```bash
npm create vite@latest my-vue-app -- --template vue-ts
cd my-vue-app
npm install
npm run dev
```

### 2.2 使用 create-vue

```bash
npm create vue@latest
# 交互式选择：TypeScript、Router、Pinia、ESLint 等
```

### 2.3 项目结构

```
my-vue-app/
├── public/              # 静态资源
├── src/
│   ├── assets/          # 资源
│   ├── components/      # 组件
│   ├── views/           # 页面
│   ├── router/          # 路由
│   ├── stores/          # Pinia 状态
│   ├── api/             # API 请求
│   ├── utils/           # 工具函数
│   ├── App.vue          # 根组件
│   └── main.ts          # 入口
├── index.html
├── vite.config.ts
└── tsconfig.json
```

## 3. 组合式 API

### 3.1 setup 函数

```vue
<script lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'

export default {
  setup() {
    // 响应式数据
    const count = ref(0)
    const state = reactive({ name: 'Vue', version: 3 })

    // 计算属性
    const double = computed(() => count.value * 2)

    // 方法
    function increment() {
      count.value++
    }

    // 生命周期
    onMounted(() => {
      console.log('组件已挂载')
    })

    return { count, state, double, increment }
  }
}
</script>
```

### 3.2 `<script setup>` 语法糖

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// 响应式数据（无需 return）
const count = ref(0)
const name = ref('Vue 3')

// 计算属性
const double = computed(() => count.value * 2)

// 方法
function increment() {
  count.value++
}

// 生命周期
onMounted(() => {
  console.log('组件已挂载')
})
</script>

<template>
  <button @click="increment">{{ count }} (双倍: {{ double }})</button>
</template>
```

## 4. 响应式系统

### 4.1 ref

用于基本类型，访问需 `.value`：

```typescript
import { ref } from 'vue'

const count = ref(0)
const name = ref<string>('Vue')
const items = ref<string[]>([])

// 修改
count.value++
items.value.push('new item')

// 模板中自动解包，无需 .value
// <div>{{ count }}</div>
```

### 4.2 reactive

用于对象，直接访问属性：

```typescript
import { reactive } from 'vue'

const state = reactive({
  user: { name: 'Alice', age: 25 },
  list: [1, 2, 3]
})

// 直接修改
state.user.age = 26
state.list.push(4)
```

### 4.3 ref vs reactive

```typescript
// ref: 适合基本类型，或需要重新赋值的对象
const count = ref(0)
count.value = 10  // 可以重新赋值

// reactive: 适合对象，但不能整体替换
const state = reactive({ count: 0 })
state.count = 10            // ✓
// state = { count: 10 }    // ✗ 失去响应性

// 解决：用 reactive 包裹属性
const state = reactive({
  data: { count: 0 }
})
state.data = { count: 10 }  // ✓
```

### 4.4 computed

```typescript
import { ref, computed } from 'vue'

const firstName = ref('张')
const lastName = ref('三')

// 只读
const fullName = computed(() => `${firstName.value}${lastName.value}`)

// 可写
const fullNameWritable = computed({
  get() {
    return `${firstName.value}${lastName.value}`
  },
  set(newValue: string) {
    firstName.value = newValue[0]
    lastName.value = newValue.slice(1)
  }
})
```

### 4.5 watch

```typescript
import { ref, watch, watchEffect } from 'vue'

const count = ref(0)
const user = reactive({ name: 'Vue', age: 3 })

// 监听 ref
watch(count, (newVal, oldVal) => {
  console.log(`count: ${oldVal} → ${newVal}`)
})

// 监听 reactive 属性（需要 getter）
watch(
  () => user.age,
  (newVal, oldVal) => {
    console.log(`age: ${oldVal} → ${newVal}`)
  }
)

// 立即执行
watch(count, (val) => {
  console.log('count:', val)
}, { immediate: true })

// 深度监听
watch(user, (newVal) => {
  console.log('user changed:', newVal)
}, { deep: true })

// watchEffect：自动收集依赖
watchEffect(() => {
  console.log(`count is ${count.value}`)
})
```

## 5. 生命周期

```typescript
import {
  onBeforeMount,
  onMounted,
  onBeforeUpdate,
  onUpdated,
  onBeforeUnmount,
  onUnmounted,
  onErrorCaptured,
} from 'vue'

onBeforeMount(() => console.log('挂载前'))
onMounted(() => console.log('已挂载'))
onBeforeUpdate(() => console.log('更新前'))
onUpdated(() => console.log('已更新'))
onBeforeUnmount(() => console.log('卸载前'))
onUnmounted(() => console.log('已卸载'))
onErrorCaptured((err) => console.log('捕获错误:', err))
```

## 6. 组件通信

### 6.1 Props

```vue
<!-- Child.vue -->
<script setup lang="ts">
interface Props {
  title: string
  count?: number  // 可选
  items?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  count: 0,
  items: () => []
})
</script>

<template>
  <h1>{{ title }}</h1>
  <p>{{ count }}</p>
</template>
```

### 6.2 Emits

```vue
<!-- Child.vue -->
<script setup lang="ts">
const emit = defineEmits<{
  (e: 'change', value: number): void
  (e: 'submit', data: { name: string }): void
}>()

function handleClick() {
  emit('change', 42)
}
</script>
```

```vue
<!-- Parent.vue -->
<script setup lang="ts">
import Child from './Child.vue'

function handleChange(val: number) {
  console.log('收到:', val)
}
</script>

<template>
  <Child @change="handleChange" />
</template>
```

### 6.3 v-model

```vue
<!-- Child.vue -->
<script setup lang="ts">
const modelValue = defineModel<string>()
</script>

<template>
  <input v-model="modelValue" />
</template>

<!-- Parent.vue -->
<Child v-model="message" />
```

### 6.4 provide/inject

```typescript
// Parent.vue
import { provide, ref } from 'vue'

const theme = ref('dark')
provide('theme', theme)

// Child.vue（深层子组件）
import { inject, Ref } from 'vue'

const theme = inject<Ref<string>>('theme', ref('light'))
```

## 7. 组合式函数（Composables）

### 7.1 自定义 Hook

```typescript
// useCounter.ts
import { ref, computed } from 'vue'

export function useCounter(initialValue: number = 0) {
  const count = ref(initialValue)
  const double = computed(() => count.value * 2)
  
  function increment() {
    count.value++
  }
  
  function decrement() {
    count.value--
  }
  
  function reset() {
    count.value = initialValue
  }
  
  return { count, double, increment, decrement, reset }
}
```

```vue
<script setup lang="ts">
import { useCounter } from './useCounter'

const { count, double, increment } = useCounter(10)
</script>
```

### 7.2 useFetch 示例

```typescript
// useFetch.ts
import { ref, watchEffect } from 'vue'

export function useFetch<T>(url: string) {
  const data = ref<T | null>(null)
  const error = ref<string | null>(null)
  const loading = ref(true)

  async function fetchData() {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(url)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      data.value = await res.json()
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  watchEffect(() => {
    fetchData()
  })

  return { data, error, loading, refresh: fetchData }
}
```

## 8. 路由（Vue Router 4）

### 8.1 安装与配置

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Home.vue')
    },
    {
      path: '/users/:id',
      name: 'user',
      component: () => import('../views/User.vue'),
      props: true
    },
    {
      path: '/admin',
      component: () => import('../views/Admin.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    return '/login'
  }
})

export default router
```

### 8.2 在组件中使用

```vue
<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 编程式导航
function goHome() {
  router.push('/')
}

function goUser(id: number) {
  router.push({ name: 'user', params: { id } })
}

// 获取当前路由参数
const userId = route.params.id
</script>
```

## 9. 状态管理（Pinia）

### 9.1 定义 Store

```typescript
// stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // state
  const user = ref<{ name: string; age: number } | null>(null)
  const token = ref<string>('')
  
  // getters
  const isLoggedIn = computed(() => !!token.value)
  const userName = computed(() => user.value?.name || '游客')
  
  // actions
  async function login(username: string, password: string) {
    const res = await api.login(username, password)
    token.value = res.token
    user.value = res.user
    localStorage.setItem('token', res.token)
  }
  
  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
  }
  
  return { user, token, isLoggedIn, userName, login, logout }
})
```

### 9.2 使用 Store

```vue
<script setup lang="ts">
import { useUserStore } from '../stores/user'
import { storeToRefs } from 'pinia'

const userStore = useUserStore()

// 解构响应式数据（需用 storeToRefs）
const { isLoggedIn, userName } = storeToRefs(userStore)

// 方法可以直接解构
const { login, logout } = userStore
</script>
```

## 10. 常用 UI 库

### 10.1 Element Plus

```bash
npm install element-plus
```

```typescript
// main.ts
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

app.use(ElementPlus)
```

### 10.2 Ant Design Vue

```bash
npm install ant-design-vue
```

### 10.3 Naive UI

```bash
npm install naive-ui
```

## 11. 性能优化

### 11.1 路由懒加载

```typescript
const routes = [
  {
    path: '/about',
    component: () => import('../views/About.vue')  // 懒加载
  }
]
```

### 11.2 v-memo

```vue
<div v-memo="[item.id, item.selected]">
  <!-- 仅当 item.id 或 item.selected 变化时才重新渲染 -->
  {{ item.content }}
</div>
```

### 11.3 shallowRef / shallowReactive

```typescript
import { shallowRef, shallowReactive } from 'vue'

// 大列表，不需要深度响应
const bigList = shallowRef<Item[]>([])

// 大对象，仅顶层响应
const bigObj = shallowReactive({ data: { ... } })
```

### 11.4 异步组件

```typescript
import { defineAsyncComponent } from 'vue'

const AsyncComp = defineAsyncComponent(() => import('./Heavy.vue'))
```

## 12. 部署

### 12.1 构建

```bash
npm run build
# 输出到 dist/
```

### 12.2 Nginx 配置

```nginx
server {
    listen 80;
    server_name example.com;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
    }
}
```

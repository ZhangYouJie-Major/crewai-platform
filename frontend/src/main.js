import './assets/main.css'

import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import App from './App.vue'
import router from './router'
import store from './store'

/**
 * 应用初始化
 * 创建Vue应用实例并配置所需的插件和组件
 */
const app = createApp(App)

// 配置Element Plus UI组件库
app.use(ElementPlus, {
  locale: zhCn,  // 设置为中文语言
  size: 'default'  // 默认组件尺寸
})

// 注册所有Element Plus图标组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 配置路由
app.use(router)

// 提供全局状态管理
app.provide('store', store)

// 全局属性和方法
app.config.globalProperties.$store = store

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('全局错误:', err, info)
  // 可以在这里添加错误上报逻辑
}

// 应用挂载前的初始化工作
async function initializeApp() {
  try {
    // 初始化应用状态
    await store.app.initialize()
    
    // 挂载应用
    app.mount('#app')
    
    console.log('CrewAI Platform 应用初始化完成')
  } catch (error) {
    console.error('应用初始化失败:', error)
    // 即使初始化失败也要挂载应用，避免白屏
    app.mount('#app')
  }
}

// 开始初始化应用
initializeApp()

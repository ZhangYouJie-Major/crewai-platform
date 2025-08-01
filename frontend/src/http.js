import axios from 'axios'
import router from './router'
import { ElMessage } from 'element-plus'

/**
 * HTTP客户端配置
 * 基于axios的HTTP请求封装，提供统一的请求和响应处理
 */
const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',  // 使用环境变量配置API基础URL
  timeout: 10000,  // 请求超时时间
  headers: {
    'Content-Type': 'application/json',
  }
})

/**
 * 请求拦截器
 * 在每个请求发送前执行，用于添加认证token等全局处理
 */
http.interceptors.request.use(
  config => {
    // 从本地存储获取访问令牌
    const access = localStorage.getItem('access')
    if (access) {
      // 在请求头中添加Authorization
      config.headers['Authorization'] = `Bearer ${access}`
    }
    
    // 可以在这里添加其他全局请求配置
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  error => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 * 处理响应数据和错误，提供统一的错误处理机制
 */
http.interceptors.response.use(
  response => {
    // 请求成功的情况下直接返回响应数据
    console.log('接收响应:', response.status, response.config.url)
    return response
  },
  async error => {
    const { response, config } = error
    
    console.error('响应错误:', error)
    
    if (response) {
      const { status } = response
      
      switch (status) {
        case 401:
          // 未授权，可能是token过期
          await handleUnauthorized()
          break
          
        case 403:
          ElMessage.error('权限不足，无法访问该资源')
          break
          
        case 404:
          ElMessage.error('请求的资源不存在')
          break
          
        case 500:
          ElMessage.error('服务器内部错误，请稍后重试')
          break
          
        default:
          // 显示服务器返回的错误信息
          const errorMessage = response.data?.detail || 
                              response.data?.message || 
                              `请求失败 (${status})`
          ElMessage.error(errorMessage)
      }
    } else if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络连接')
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

/**
 * 处理401未授权错误
 * 尝试使用refresh token刷新访问令牌，如果失败则跳转到登录页
 */
async function handleUnauthorized() {
  const refreshToken = localStorage.getItem('refresh')
  
  if (refreshToken) {
    try {
      // 尝试刷新token
      const response = await axios.post('/api/auth/refresh/', {
        refresh: refreshToken
      })
      
      const { access } = response.data
      localStorage.setItem('access', access)
      
      ElMessage.success('登录状态已刷新')
      // 可以考虑重新发送失败的请求
      
    } catch (refreshError) {
      console.error('刷新token失败:', refreshError)
      clearAuthData()
      redirectToLogin()
    }
  } else {
    clearAuthData()
    redirectToLogin()
  }
}

/**
 * 清除认证数据
 */
function clearAuthData() {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
}

/**
 * 跳转到登录页面
 */
function redirectToLogin() {
  ElMessage.warning('登录状态已过期，请重新登录')
  
  // 避免在登录页面重复跳转
  if (router.currentRoute.value.path !== '/login') {
    router.push('/login')
  }
}

/**
 * 请求重试机制（可选）
 * @param {Function} fn - 要重试的请求函数
 * @param {number} retries - 重试次数
 * @param {number} delay - 重试延迟（毫秒）
 */
export function retryRequest(fn, retries = 3, delay = 1000) {
  return new Promise((resolve, reject) => {
    const attempt = (remaining) => {
      fn()
        .then(resolve)
        .catch(error => {
          if (remaining > 0) {
            console.log(`请求失败，${delay}ms后重试，剩余重试次数：${remaining}`)
            setTimeout(() => attempt(remaining - 1), delay)
          } else {
            reject(error)
          }
        })
    }
    attempt(retries)
  })
}

export default http 
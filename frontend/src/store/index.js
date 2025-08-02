import { reactive } from 'vue'
import api from '../services/api'

/**
 * 应用状态管理 - 简化版本
 */
const state = reactive({
  // 用户相关状态
  user: {
    info: null,
    isLoggedIn: false,
    roles: []
  },
  
  // 应用状态
  app: {
    loading: false,
    sidebarCollapsed: false
  },

  // 数据缓存
  cache: {
    users: [],
    roles: [],
    permissions: [],
    dashboardStats: null
  }
})

/**
 * 用户操作
 */
const userActions = {
  async login(credentials) {
    try {
      state.app.loading = true
      const response = await api.login(credentials)
      const { access, refresh, user } = response.data
      
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
      
      state.user.info = user
      state.user.isLoggedIn = true
      state.user.roles = user.roles || []
      
      return response
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    } finally {
      state.app.loading = false
    }
  },

  async logout() {
    try {
      const refreshToken = localStorage.getItem('refresh')
      if (refreshToken) {
        await api.logout(refreshToken)
      }
    } catch (error) {
      console.error('登出请求失败:', error)
    } finally {
      this.clearUserData()
    }
  },

  async register(userData) {
    try {
      state.app.loading = true
      const response = await api.register(userData)
      const { access, refresh, user } = response.data
      
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
      
      state.user.info = user
      state.user.isLoggedIn = true
      
      return response
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    } finally {
      state.app.loading = false
    }
  },

  async fetchCurrentUser() {
    try {
      const response = await api.getCurrentUser()
      state.user.info = response.data
      state.user.isLoggedIn = true
      state.user.roles = response.data.roles || []
      return response
    } catch (error) {
      console.error('获取用户信息失败:', error)
      this.clearUserData()
      throw error
    }
  },

  clearUserData() {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    state.user.info = null
    state.user.isLoggedIn = false
    state.user.roles = []
  },

  hasRole(roleName) {
    return state.user.roles.some(r => r.name === roleName)
  }
}

/**
 * 数据缓存操作
 */
const cacheActions = {
  async fetchDashboardStats(refresh = false) {
    if (!refresh && state.cache.dashboardStats) {
      return state.cache.dashboardStats
    }
    
    try {
      const response = await api.getDashboardStats()
      state.cache.dashboardStats = response.data
      return state.cache.dashboardStats
    } catch (error) {
      console.error('获取仪表盘数据失败:', error)
      throw error
    }
  },

  async fetchUsers(refresh = false) {
    if (!refresh && state.cache.users.length > 0) {
      return state.cache.users
    }
    
    try {
      const response = await api.getUsers()
      state.cache.users = response.data.results || response.data
      return state.cache.users
    } catch (error) {
      console.error('获取用户列表失败:', error)
      throw error
    }
  },

  async fetchRoles(refresh = false) {
    if (!refresh && state.cache.roles.length > 0) {
      return state.cache.roles
    }
    
    try {
      const response = await api.getRoles()
      state.cache.roles = response.data.results || response.data
      return state.cache.roles
    } catch (error) {
      console.error('获取角色列表失败:', error)
      throw error
    }
  },

  async fetchPermissions(refresh = false) {
    if (!refresh && state.cache.permissions.length > 0) {
      return state.cache.permissions
    }
    
    try {
      const response = await api.getPermissions()
      state.cache.permissions = response.data.results || response.data
      return state.cache.permissions
    } catch (error) {
      console.error('获取权限列表失败:', error)
      throw error
    }
  },

  clearCache() {
    state.cache.users = []
    state.cache.roles = []
    state.cache.permissions = []
    state.cache.dashboardStats = null
  }
}

/**
 * 应用操作
 */
const appActions = {
  setLoading(loading) {
    state.app.loading = loading
  },

  toggleSidebar() {
    state.app.sidebarCollapsed = !state.app.sidebarCollapsed
  },

  async initialize() {
    const token = localStorage.getItem('access')
    if (token) {
      try {
        await userActions.fetchCurrentUser()
        console.log('应用初始化成功，用户已登录')
      } catch (error) {
        console.warn('应用初始化时获取用户信息失败，清除本地token:', error.message)
        // 静默清理无效的token，不抛出错误
        userActions.clearUserData()
      }
    } else {
      console.log('应用初始化完成，用户未登录')
    }
  }
}

/**
 * 导出状态管理对象
 */
const store = {
  state,
  user: userActions,
  cache: cacheActions,
  app: appActions
}

export default store
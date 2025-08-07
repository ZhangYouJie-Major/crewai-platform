import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import Dashboard from '../views/Dashboard.vue'
import UserManagement from '../views/UserManagement.vue'
import RoleManagement from '../views/RoleManagement.vue'
import PermissionManagement from '../views/PermissionManagement.vue'
import RolePermission from '../views/RolePermission.vue'
import LLMModelManagement from '../views/LLMModelManagement.vue'
import AgentManagement from '../views/AgentManagement.vue'
import DictionaryManagement from '../views/DictionaryManagement.vue'
import MCPToolManagement from '../views/MCPToolManagement.vue'
import ChatInterface from '../views/ChatInterface.vue'

// 检查是否已登录
const isAuthenticated = () => {
  const accessToken = localStorage.getItem('access')
  const refreshToken = localStorage.getItem('refresh')
  
  console.log('检查认证状态:', { 
    hasAccess: !!accessToken, 
    hasRefresh: !!refreshToken,
    accessLength: accessToken?.length,
    currentPath: window.location.pathname
  })
  
  // 只要有access token就认为已登录，让HTTP拦截器处理过期问题
  return !!accessToken
}

const routes = [
  { 
    path: '/login', 
    component: Login,
    beforeEnter: (to, from, next) => {
      if (isAuthenticated()) {
        next('/')
      } else {
        next()
      }
    }
  },
  { path: '/register', component: Register },
  {
    path: '/',
    component: Home,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: '/dashboard', component: Dashboard },
      { path: '/users', component: UserManagement },
      { path: '/roles', component: RoleManagement },
      { path: '/permissions', component: PermissionManagement },
      { path: '/rbac', component: RolePermission },
      { path: '/llm-models', component: LLMModelManagement },
      { path: '/agents', component: AgentManagement },
      { path: '/mcp-tools', component: MCPToolManagement },
      { path: '/dictionaries', component: DictionaryManagement },
      { path: '/chat', component: ChatInterface },
    ]
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  console.log('路由守卫执行:', { 
    to: to.path, 
    from: from.path, 
    requiresAuth: to.matched.some(record => record.meta.requiresAuth)
  })
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const authenticated = isAuthenticated()
    console.log('需要认证的路由，认证状态:', authenticated)
    
    if (!authenticated) {
      console.log('未认证，跳转到登录页')
      next('/login')
    } else {
      console.log('已认证，允许访问')
      next()
    }
  } else {
    console.log('不需要认证的路由，直接访问')
    next()
  }
})

export default router 
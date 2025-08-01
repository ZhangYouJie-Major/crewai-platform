import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import Dashboard from '../views/Dashboard.vue'
import UserManagement from '../views/UserManagement.vue'
import RoleManagement from '../views/RoleManagement.vue'
import PermissionManagement from '../views/PermissionManagement.vue'
import RolePermission from '../views/RolePermission.vue'

// 检查是否已登录
const isAuthenticated = () => {
  return localStorage.getItem('access') !== null
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
    ]
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated()) {
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router 
<template>
  <div class="home-container">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <h1>CrewAI 开发平台</h1>
          <div class="user-info">
            <el-dropdown @command="handleUserCommand">
              <span class="el-dropdown-link">
                {{ userInfo.username }}
                <el-icon class="el-icon--right">
                  <arrow-down />
                </el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                  <el-dropdown-item command="rbac" v-if="hasPermission('rbac.manage')">权限管理</el-dropdown-item>
                  <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-container>
        <el-aside width="200px" class="sidebar">
          <el-menu
            :default-active="$route.path"
            class="sidebar-menu"
            @select="handleMenuSelect"
            router
          >
            <el-menu-item index="/dashboard">
              <el-icon><House /></el-icon>
              <span>仪表盘</span>
            </el-menu-item>
            <el-menu-item index="/users">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="/roles">
              <el-icon><Avatar /></el-icon>
              <span>角色管理</span>
            </el-menu-item>
            <el-menu-item index="/permissions">
              <el-icon><Key /></el-icon>
              <span>权限管理</span>
            </el-menu-item>
            <el-menu-item index="/rbac">
              <el-icon><Setting /></el-icon>
              <span>角色权限</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../http'
import { 
  House, 
  User, 
  UserFilled,
  ArrowDown,
  Avatar,
  Key,
  Setting
} from '@element-plus/icons-vue'

const router = useRouter()
const userInfo = ref({})
const activeMenu = ref('/dashboard')

// 检查用户权限的函数（简化版）
const hasPermission = (permission) => {
  // 实际项目中这里应该根据用户角色和权限进行判断
  // 现在简化处理，假设管理员有所有权限
  return userInfo.value.is_staff || false
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const { data } = await http.get('/auth/me/')
    userInfo.value = data
  } catch (error) {
    ElMessage.error('获取用户信息失败')
  }
}

// 处理用户菜单命令
const handleUserCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'rbac':
      router.push('/rbac')
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 处理菜单选择
const handleMenuSelect = (index) => {
  router.push(index)
}

// 退出登录
const handleLogout = async () => {
  try {
    const refresh = localStorage.getItem('refresh')
    if (refresh) {
      await http.post('/auth/logout/', { refresh })
    }
  } catch (error) {
    // 忽略退出登录时的错误
  } finally {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    router.push('/login')
  }
}

// 组件挂载时获取用户信息
onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped>
.home-container {
  width: 100vw;
  height: 100vh;
}

.home-container .el-container {
  height: 100%;
}

.header {
  background-color: #409eff;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.user-info {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
}

.sidebar {
  background-color: #f5f5f5;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-menu {
  border: none;
  height: 100%;
}

.main-content {
  padding: 20px;
  background-color: #f0f2f5;
  overflow-y: auto;
  height: calc(100vh - 60px); /* 减去header高度 */
}
</style>
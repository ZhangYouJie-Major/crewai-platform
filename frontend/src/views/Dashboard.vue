<template>
  <div class="dashboard">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <h2>{{ welcomeMessage }}</h2>
          <el-button type="primary" @click="refreshData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </template>
      <p>欢迎使用CrewAI平台权限管理系统，请从左侧菜单选择功能模块</p>
    </el-card>
    
    <!-- 统计数据卡片 -->
    <el-row :gutter="20" class="stats-row" v-loading="loading">
      <el-col :span="8">
        <el-card class="stat-card user-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="48"><User /></el-icon>
            </div>
            <div class="stat-info">
              <h3>用户总数</h3>
              <p class="stat-number">{{ stats.userCount }}</p>
              <el-tag size="small" type="info">活跃用户</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stat-card role-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="48"><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <h3>角色总数</h3>
              <p class="stat-number">{{ stats.roleCount }}</p>
              <el-tag size="small" type="success">系统角色</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stat-card permission-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="48"><Key /></el-icon>
            </div>
            <div class="stat-info">
              <h3>权限总数</h3>
              <p class="stat-number">{{ stats.permissionCount }}</p>
              <el-tag size="small" type="warning">功能权限</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作区域 -->
    <el-card class="quick-actions-card">
      <template #header>
        <h3>快捷操作</h3>
      </template>
      <el-row :gutter="16">
        <el-col :span="6">
          <el-button 
            type="primary" 
            size="large" 
            @click="navigateTo('/users')"
            style="width: 100%"
          >
            <el-icon><User /></el-icon>
            用户管理
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button 
            type="success" 
            size="large" 
            @click="navigateTo('/roles')"
            style="width: 100%"
          >
            <el-icon><UserFilled /></el-icon>
            角色管理
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button 
            type="warning" 
            size="large" 
            @click="navigateTo('/permissions')"
            style="width: 100%"
          >
            <el-icon><Key /></el-icon>
            权限管理
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button 
            type="info" 
            size="large" 
            @click="navigateTo('/rbac')"
            style="width: 100%"
          >
            <el-icon><Setting /></el-icon>
            权限配置
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 最近活动 -->
    <el-card class="recent-activity-card">
      <template #header>
        <h3>系统概览</h3>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
        <el-descriptions-item label="运行环境">开发环境</el-descriptions-item>
        <el-descriptions-item label="当前用户">{{ currentUser?.username || '未登录' }}</el-descriptions-item>
        <el-descriptions-item label="用户角色">
          <el-tag 
            v-for="role in currentUser?.roles" 
            :key="role.id" 
            size="small"
            style="margin-right: 4px"
          >
            {{ role.name }}
          </el-tag>
          <span v-if="!currentUser?.roles?.length">暂无角色</span>
        </el-descriptions-item>
        <el-descriptions-item label="最后登录">{{ formatDate(currentUser?.last_login) }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ formatDate(currentUser?.date_joined) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, UserFilled, Key, Setting, Refresh } from '@element-plus/icons-vue'
import store from '../store'

// 组件状态
const loading = ref(false)
const stats = ref({
  userCount: 0,
  roleCount: 0, 
  permissionCount: 0
})

// 路由实例
const router = useRouter()

// 计算属性
const currentUser = computed(() => store.state.user.info)
const welcomeMessage = computed(() => {
  const user = currentUser.value
  if (user) {
    const timeGreeting = getTimeGreeting()
    return `${timeGreeting}，${user.first_name || user.username}！`
  }
  return '欢迎使用CrewAI平台'
})

/**
 * 获取时间段问候语
 */
function getTimeGreeting() {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨好'
  if (hour < 9) return '早上好'  
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 17) return '下午好'
  if (hour < 19) return '傍晚好'
  return '晚上好'
}

/**
 * 格式化日期
 */
function formatDate(dateString) {
  if (!dateString) return '暂无记录'
  return new Date(dateString).toLocaleString('zh-CN')
}

/**
 * 导航到指定页面
 */
function navigateTo(path) {
  router.push(path)
}

/**
 * 加载统计数据
 */
async function loadStats() {
  try {
    loading.value = true
    const data = await store.cache.fetchDashboardStats()
    stats.value = data
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

/**
 * 刷新数据
 */
async function refreshData() {
  try {
    loading.value = true
    // 清除缓存并重新加载
    store.cache.clearCache()
    await loadStats()
    ElMessage.success('数据刷新成功')
  } catch (error) {
    console.error('刷新数据失败:', error)
    ElMessage.error('刷新数据失败')
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 60px);
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
  font-weight: 500;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  transition: all 0.3s ease;
  border-radius: 8px;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.stat-icon {
  margin-right: 16px;
  padding: 12px;
  border-radius: 50%;
  background-color: #f0f2f5;
}

.user-card .stat-icon {
  color: #409eff;
  background-color: #ecf5ff;
}

.role-card .stat-icon {
  color: #67c23a;
  background-color: #f0f9ff;
}

.permission-card .stat-icon {
  color: #e6a23c;
  background-color: #fdf6ec;
}

.stat-info h3 {
  margin: 0 0 8px 0;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.stat-number {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.quick-actions-card {
  margin-bottom: 20px;
}

.quick-actions-card h3 {
  margin: 0;
  color: #303133;
  font-weight: 500;
}

.recent-activity-card h3 {
  margin: 0;
  color: #303133;
  font-weight: 500;
}

.el-button {
  border-radius: 6px;
}

.el-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .stat-content {
    flex-direction: column;
    text-align: center;
  }
  
  .stat-icon {
    margin-right: 0;
    margin-bottom: 10px;
  }
}
</style>
<template>
  <div class="login-container">
    <div class="login-box">
      <el-card class="login-card">
        <h2 class="login-title">用户登录</h2>
        <el-form :model="loginForm" :rules="rules" ref="formRef" label-width="80px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="loginForm.username" autocomplete="off" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="loginForm.password" type="password" autocomplete="off" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="onLogin" :loading="loading" class="login-button">登录</el-button>
          </el-form-item>
        </el-form>
        <div class="register-link">
          <el-button type="text" @click="$router.push('/register')">没有账号？立即注册</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../http'

const router = useRouter()
const loginForm = ref({ username: '', password: '' })
const loading = ref(false)
const formRef = ref(null)
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const onLogin = () => {
  formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const { data } = await http.post('/auth/login/', {
        username: loginForm.value.username,
        password: loginForm.value.password
      })
      if (data.access) {
        localStorage.setItem('access', data.access)
        localStorage.setItem('refresh', data.refresh)
        ElMessage.success('登录成功')
        router.push('/')
      } else {
        ElMessage.error(data.detail || '登录失败')
      }
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '登录失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  padding: 20px;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.2) 0%, transparent 50%);
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.login-box {
  width: 100%;
  max-width: 400px;
  z-index: 1;
  position: relative;
}

.login-card {
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 2px 16px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 40px 30px;
}

.login-title {
  text-align: center;
  margin-bottom: 40px;
  color: #333;
  font-size: 28px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.register-link {
  text-align: center;
  margin-top: 30px;
}

.register-link .el-button {
  color: #667eea;
  font-weight: 500;
}

.register-link .el-button:hover {
  color: #764ba2;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
  }
  
  .login-title {
    font-size: 24px;
    margin-bottom: 30px;
  }
}
</style> 
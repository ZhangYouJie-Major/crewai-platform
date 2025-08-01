<template>
  <div class="register-container">
    <div class="register-box">
      <el-card class="register-card">
        <h2 class="register-title">用户注册</h2>
        <el-form :model="registerForm" :rules="rules" ref="formRef" label-width="80px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="registerForm.username" autocomplete="off" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="registerForm.email" autocomplete="off" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="registerForm.password" type="password" autocomplete="off" />
          </el-form-item>
          <el-form-item label="确认密码" prop="password_confirm">
            <el-input v-model="registerForm.password_confirm" type="password" autocomplete="off" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="onRegister" :loading="loading" class="register-button">注册</el-button>
          </el-form-item>
        </el-form>
        <div class="login-link">
          <el-button type="text" @click="$router.push('/login')">已有账号？立即登录</el-button>
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
const registerForm = ref({ username: '', email: '', password: '', password_confirm: '' })
const loading = ref(false)
const formRef = ref(null)

const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
    return
  }
  
  // 检查长度
  if (value.length < 8) {
    callback(new Error('密码至少需要8位字符'))
    return
  }
  
  // 检查是否包含字母
  if (!/[a-zA-Z]/.test(value)) {
    callback(new Error('密码必须包含字母'))
    return
  }
  
  // 检查是否包含数字
  if (!/\d/.test(value)) {
    callback(new Error('密码必须包含数字'))
    return
  }
  
  // 检查是否与用户名相似
  if (registerForm.value.username && value.toLowerCase().includes(registerForm.value.username.toLowerCase())) {
    callback(new Error('密码不能包含用户名'))
    return
  }
  
  // 检查是否为常见密码
  const commonPasswords = ['12345678', 'password', '87654321', 'qwerty123', 'abc12345', '123456789']
  if (commonPasswords.includes(value.toLowerCase())) {
    callback(new Error('密码过于简单，请使用更复杂的密码'))
    return
  }
  
  // 检查是否为纯数字
  if (/^\d+$/.test(value)) {
    callback(new Error('密码不能为纯数字'))
    return
  }
  
  callback()
}

const validatePasswordConfirm = (rule, value, callback) => {
  if (value !== registerForm.value.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { validator: validatePassword, trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePasswordConfirm, trigger: 'blur' }
  ]
}

const onRegister = () => {
  formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const { data } = await http.post('/auth/register/', registerForm.value)
      if (data.access) {
        localStorage.setItem('access', data.access)
        localStorage.setItem('refresh', data.refresh)
        ElMessage.success('注册成功')
        router.push('/')
      } else {
        ElMessage.error(data.detail || '注册失败')
      }
    } catch (e) {
      console.error('注册错误:', e)
      const errorData = e.response?.data
      
      if (errorData && errorData.errors) {
        // 处理字段级验证错误
        let errorMessages = []
        for (const [field, messages] of Object.entries(errorData.errors)) {
          if (Array.isArray(messages)) {
            errorMessages = errorMessages.concat(messages)
          } else {
            errorMessages.push(messages)
          }
        }
        
        if (errorMessages.length > 0) {
          // 显示第一个错误信息
          ElMessage.error(errorMessages[0])
        } else {
          ElMessage.error(errorData.detail || '注册失败')
        }
      } else {
        // 显示通用错误信息
        ElMessage.error(errorData?.detail || '注册失败，请稍后重试')
      }
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  padding: 20px;
}

.register-container::before {
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

.register-box {
  width: 100%;
  max-width: 400px;
  z-index: 1;
  position: relative;
}

.register-card {
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

.register-title {
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

.register-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.login-link {
  text-align: center;
  margin-top: 30px;
}

.login-link .el-button {
  color: #667eea;
  font-weight: 500;
}

.login-link .el-button:hover {
  color: #764ba2;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .register-card {
    padding: 30px 20px;
  }
  
  .register-title {
    font-size: 24px;
    margin-bottom: 30px;
  }
}
</style> 
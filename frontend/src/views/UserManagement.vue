<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showAddDialog">添加用户</el-button>
        </div>
      </template>
      
      <el-table :data="users" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="first_name" label="姓名" />
        <el-table-column prop="is_active" label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="注册时间">
          <template #default="scope">
            {{ formatDate(scope.row.date_joined) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editUser(scope.row)">编辑</el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deleteUser(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="fetchUsers"
        style="margin-top: 20px; text-align: right;"
      />
    </el-card>

    <!-- 添加/编辑用户对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="userForm" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" type="email" />
        </el-form-item>
        <el-form-item label="姓名" prop="first_name">
          <el-input v-model="userForm.first_name" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../http'

const users = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('添加用户')
const formRef = ref()

const userForm = ref({
  username: '',
  email: '',
  first_name: '',
  password: '',
  is_active: true
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

const fetchUsers = async (page = 1) => {
  loading.value = true
  try {
    const { data } = await http.get('/users/', {
      params: { page, page_size: pageSize.value }
    })
    users.value = data.results || data
    total.value = data.count || data.length
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  isEdit.value = false
  dialogTitle.value = '添加用户'
  userForm.value = {
    username: '',
    email: '',
    first_name: '',
    password: '',
    is_active: true
  }
  dialogVisible.value = true
}

const editUser = (user) => {
  isEdit.value = true
  dialogTitle.value = '编辑用户'
  userForm.value = { ...user }
  dialogVisible.value = true
}

const saveUser = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    if (isEdit.value) {
      await http.put(`/users/${userForm.value.id}/`, userForm.value)
      ElMessage.success('用户更新成功')
    } else {
      await http.post('/users/', userForm.value)
      ElMessage.success('用户创建成功')
    }
    
    dialogVisible.value = false
    fetchUsers(currentPage.value)
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 ${user.username} 吗？`, '提示', {
      type: 'warning'
    })
    
    await http.delete(`/users/${user.id}/`)
    ElMessage.success('用户删除成功')
    fetchUsers(currentPage.value)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
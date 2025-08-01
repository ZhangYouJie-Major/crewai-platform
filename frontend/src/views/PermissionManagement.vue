<template>
  <div class="permission-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>权限管理</span>
          <el-button type="primary" @click="showAddDialog">添加权限</el-button>
        </div>
      </template>
      
      <el-table :data="permissions" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="权限名称" />
        <el-table-column prop="codename" label="权限标识" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editPermission(scope.row)">编辑</el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deletePermission(scope.row)"
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
        @current-change="fetchPermissions"
        style="margin-top: 20px; text-align: right;"
      />
    </el-card>

    <!-- 添加/编辑权限对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="permissionForm" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="permissionForm.name" />
        </el-form-item>
        <el-form-item label="权限标识" prop="codename">
          <el-input v-model="permissionForm.codename" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="permissionForm.description" 
            type="textarea" 
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePermission">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../http'

const permissions = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const dialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('添加权限')
const formRef = ref()

const permissionForm = ref({
  name: '',
  codename: '',
  description: ''
})

const rules = {
  name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' }
  ],
  codename: [
    { required: true, message: '请输入权限标识', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_\.]+$/, message: '权限标识只能包含字母、数字、下划线和点', trigger: 'blur' }
  ]
}

const fetchPermissions = async (page = 1) => {
  loading.value = true
  try {
    const { data } = await http.get('/permissions/', {
      params: { page, page_size: pageSize.value }
    })
    permissions.value = data.results || data
    total.value = data.count || data.length
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  isEdit.value = false
  dialogTitle.value = '添加权限'
  permissionForm.value = {
    name: '',
    codename: '',
    description: ''
  }
  dialogVisible.value = true
}

const editPermission = (permission) => {
  isEdit.value = true
  dialogTitle.value = '编辑权限'
  permissionForm.value = { ...permission }
  dialogVisible.value = true
}

const savePermission = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    if (isEdit.value) {
      await http.put(`/permissions/${permissionForm.value.id}/`, permissionForm.value)
      ElMessage.success('权限更新成功')
    } else {
      await http.post('/permissions/', permissionForm.value)
      ElMessage.success('权限创建成功')
    }
    
    dialogVisible.value = false
    fetchPermissions(currentPage.value)
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deletePermission = async (permission) => {
  try {
    await ElMessageBox.confirm(`确定要删除权限 ${permission.name} 吗？`, '提示', {
      type: 'warning'
    })
    
    await http.delete(`/permissions/${permission.id}/`)
    ElMessage.success('权限删除成功')
    fetchPermissions(currentPage.value)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchPermissions()
})
</script>

<style scoped>
.permission-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
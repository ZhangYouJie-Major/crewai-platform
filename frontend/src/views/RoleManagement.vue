<template>
  <div class="role-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色管理</span>
          <el-button type="primary" @click="showAddDialog">添加角色</el-button>
        </div>
      </template>
      
      <el-table :data="roles" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="权限数量" width="120">
          <template #default="scope">
            <el-tag type="info">{{ getPermissionCount(scope.row.id) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="scope">
            <el-button size="small" @click="editRole(scope.row)">编辑</el-button>
            <el-button 
              size="small" 
              type="warning"
              @click="managePermissions(scope.row)"
            >
              权限配置
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deleteRole(scope.row)"
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
        @current-change="fetchRoles"
        style="margin-top: 20px; text-align: right;"
      />
    </el-card>

    <!-- 添加/编辑角色对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="roleForm" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="roleForm.description" 
            type="textarea" 
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRole">确定</el-button>
      </template>
    </el-dialog>

    <!-- 权限配置对话框 -->
    <el-dialog v-model="permissionDialogVisible" title="权限配置" width="600px">
      <div v-if="currentRole">
        <h4>为角色 "{{ currentRole.name }}" 配置权限：</h4>
        <el-transfer
          v-model="selectedPermissions"
          :data="allPermissions"
          :titles="['可用权限', '已分配权限']"
          :button-texts="['移除', '添加']"
          :format="{
            noChecked: '${total}',
            hasChecked: '${checked}/${total}'
          }"
          filterable
          filter-placeholder="搜索权限"
        />
      </div>
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRolePermissions">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../http'

const roles = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const dialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const isEdit = ref(false)
const dialogTitle = ref('添加角色')
const formRef = ref()
const currentRole = ref(null)

const roleForm = ref({
  name: '',
  description: ''
})

const allPermissions = ref([])
const selectedPermissions = ref([])
const rolePermissions = ref([])

const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' }
  ]
}

const fetchRoles = async (page = 1) => {
  loading.value = true
  try {
    const { data } = await http.get('/roles/', {
      params: { page, page_size: pageSize.value }
    })
    roles.value = data.results || data
    total.value = data.count || data.length
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  } finally {
    loading.value = false
  }
}

const fetchPermissions = async () => {
  try {
    const { data } = await http.get('/permissions/')
    allPermissions.value = (data.results || data).map(permission => ({
      key: permission.id,
      label: `${permission.name} (${permission.codename})`,
      disabled: false
    }))
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  }
}

const fetchRolePermissions = async () => {
  try {
    const { data } = await http.get('/role-permissions/')
    rolePermissions.value = data.results || data
  } catch (error) {
    ElMessage.error('获取角色权限关系失败')
  }
}

const getPermissionCount = (roleId) => {
  return rolePermissions.value.filter(rp => rp.role === roleId).length
}

const showAddDialog = () => {
  isEdit.value = false
  dialogTitle.value = '添加角色'
  roleForm.value = {
    name: '',
    description: ''
  }
  dialogVisible.value = true
}

const editRole = (role) => {
  isEdit.value = true
  dialogTitle.value = '编辑角色'
  roleForm.value = { ...role }
  dialogVisible.value = true
}

const saveRole = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    if (isEdit.value) {
      await http.put(`/roles/${roleForm.value.id}/`, roleForm.value)
      ElMessage.success('角色更新成功')
    } else {
      await http.post('/roles/', roleForm.value)
      ElMessage.success('角色创建成功')
    }
    
    dialogVisible.value = false
    fetchRoles(currentPage.value)
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deleteRole = async (role) => {
  try {
    await ElMessageBox.confirm(`确定要删除角色 ${role.name} 吗？`, '提示', {
      type: 'warning'
    })
    
    await http.delete(`/roles/${role.id}/`)
    ElMessage.success('角色删除成功')
    fetchRoles(currentPage.value)
    fetchRolePermissions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const managePermissions = (role) => {
  currentRole.value = role
  const currentRolePermissions = rolePermissions.value
    .filter(rp => rp.role === role.id)
    .map(rp => rp.permission)
  selectedPermissions.value = currentRolePermissions
  permissionDialogVisible.value = true
}

const saveRolePermissions = async () => {
  if (!currentRole.value) return
  
  try {
    // 获取当前角色的权限
    const currentRolePermissions = rolePermissions.value
      .filter(rp => rp.role === currentRole.value.id)
      .map(rp => rp.permission)
    
    // 找出需要添加的权限
    const toAdd = selectedPermissions.value.filter(
      permId => !currentRolePermissions.includes(permId)
    )
    
    // 找出需要删除的权限
    const toRemove = currentRolePermissions.filter(
      permId => !selectedPermissions.value.includes(permId)
    )
    
    // 添加新权限
    for (const permissionId of toAdd) {
      await http.post('/role-permissions/', {
        role: currentRole.value.id,
        permission: permissionId
      })
    }
    
    // 删除权限
    for (const permissionId of toRemove) {
      const rolePermission = rolePermissions.value.find(
        rp => rp.role === currentRole.value.id && rp.permission === permissionId
      )
      if (rolePermission) {
        await http.delete(`/role-permissions/${rolePermission.id}/`)
      }
    }
    
    ElMessage.success('权限配置保存成功')
    permissionDialogVisible.value = false
    fetchRolePermissions()
  } catch (error) {
    ElMessage.error('保存权限配置失败')
  }
}

onMounted(() => {
  fetchRoles()
  fetchPermissions()
  fetchRolePermissions()
})
</script>

<style scoped>
.role-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
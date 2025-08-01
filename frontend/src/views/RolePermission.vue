<template>
  <div class="role-permission-container">
    <el-tabs v-model="activeTab" class="role-permission-tabs">
      <!-- 角色管理 -->
      <el-tab-pane label="角色管理" name="roles">
        <div class="tab-content">
          <div class="toolbar">
            <el-button type="primary" @click="openRoleDialog()">添加角色</el-button>
          </div>
          <el-table :data="roles" style="width: 100%" v-loading="loading.roles">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="角色名称" />
            <el-table-column prop="description" label="描述" />
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="openRoleDialog(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteRole(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 权限管理 -->
      <el-tab-pane label="权限管理" name="permissions">
        <div class="tab-content">
          <div class="toolbar">
            <el-button type="primary" @click="openPermissionDialog()">添加权限</el-button>
          </div>
          <el-table :data="permissions" style="width: 100%" v-loading="loading.permissions">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="权限名称" />
            <el-table-column prop="codename" label="权限代码" />
            <el-table-column prop="description" label="描述" />
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="openPermissionDialog(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deletePermission(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 用户角色分配 -->
      <el-tab-pane label="用户角色分配" name="user-roles">
        <div class="tab-content">
          <div class="toolbar">
            <el-button type="primary" @click="openUserRoleDialog()">分配角色</el-button>
          </div>
          <el-table :data="userRoles" style="width: 100%" v-loading="loading.userRoles">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="user_username" label="用户名" />
            <el-table-column prop="role_name" label="角色" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" type="danger" @click="deleteUserRole(scope.row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 角色权限分配 -->
      <el-tab-pane label="角色权限分配" name="role-permissions">
        <div class="tab-content">
          <div class="toolbar">
            <el-button type="primary" @click="openRolePermissionDialog()">分配权限</el-button>
          </div>
          <el-table :data="rolePermissions" style="width: 100%" v-loading="loading.rolePermissions">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="role_name" label="角色" />
            <el-table-column prop="permission_name" label="权限" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" type="danger" @click="deleteRolePermission(scope.row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 角色对话框 -->
    <el-dialog v-model="roleDialogVisible" :title="roleForm.id ? '编辑角色' : '添加角色'" width="500px">
      <el-form :model="roleForm" :rules="roleRules" ref="roleFormRef" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="roleForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="roleDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRole">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 权限对话框 -->
    <el-dialog v-model="permissionDialogVisible" :title="permissionForm.id ? '编辑权限' : '添加权限'" width="500px">
      <el-form :model="permissionForm" :rules="permissionRules" ref="permissionFormRef" label-width="100px">
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="permissionForm.name" />
        </el-form-item>
        <el-form-item label="权限代码" prop="codename">
          <el-input v-model="permissionForm.codename" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="permissionForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="permissionDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="savePermission">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 用户角色对话框 -->
    <el-dialog v-model="userRoleDialogVisible" title="分配用户角色" width="500px">
      <el-form :model="userRoleForm" :rules="userRoleRules" ref="userRoleFormRef" label-width="100px">
        <el-form-item label="用户" prop="user">
          <el-select v-model="userRoleForm.user" filterable placeholder="请选择用户">
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userRoleForm.role" placeholder="请选择角色">
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="userRoleDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUserRole">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 角色权限对话框 -->
    <el-dialog v-model="rolePermissionDialogVisible" title="分配角色权限" width="500px">
      <el-form :model="rolePermissionForm" :rules="rolePermissionRules" ref="rolePermissionFormRef" label-width="100px">
        <el-form-item label="角色" prop="role">
          <el-select v-model="rolePermissionForm.role" placeholder="请选择角色">
            <el-option
              v-for="role in roles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="权限" prop="permission">
          <el-select v-model="rolePermissionForm.permission" filterable placeholder="请选择权限">
            <el-option
              v-for="permission in permissions"
              :key="permission.id"
              :label="permission.name"
              :value="permission.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="rolePermissionDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRolePermission">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../http'

// 标签页控制
const activeTab = ref('roles')

// 数据存储
const roles = ref([])
const permissions = ref([])
const userRoles = ref([])
const rolePermissions = ref([])
const users = ref([])

// 加载状态
const loading = reactive({
  roles: false,
  permissions: false,
  userRoles: false,
  rolePermissions: false
})

// 对话框控制
const roleDialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const userRoleDialogVisible = ref(false)
const rolePermissionDialogVisible = ref(false)

// 表单数据
const roleForm = reactive({ id: null, name: '', description: '' })
const permissionForm = reactive({ id: null, name: '', codename: '', description: '' })
const userRoleForm = reactive({ id: null, user: null, role: null })
const rolePermissionForm = reactive({ id: null, role: null, permission: null })

// 表单引用
const roleFormRef = ref(null)
const permissionFormRef = ref(null)
const userRoleFormRef = ref(null)
const rolePermissionFormRef = ref(null)

// 表单验证规则
const roleRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
}

const permissionRules = {
  name: [{ required: true, message: '请输入权限名称', trigger: 'blur' }],
  codename: [{ required: true, message: '请输入权限代码', trigger: 'blur' }]
}

const userRoleRules = {
  user: [{ required: true, message: '请选择用户', trigger: 'change' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const rolePermissionRules = {
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  permission: [{ required: true, message: '请选择权限', trigger: 'change' }]
}

// 获取所有数据
const fetchData = async () => {
  await Promise.all([
    fetchRoles(),
    fetchPermissions(),
    fetchUserRoles(),
    fetchRolePermissions(),
    fetchUsers()
  ])
}

// 获取角色列表
const fetchRoles = async () => {
  loading.roles = true
  try {
    const { data } = await http.get('/roles/')
    roles.value = data.results || data
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  } finally {
    loading.roles = false
  }
}

// 获取权限列表
const fetchPermissions = async () => {
  loading.permissions = true
  try {
    const { data } = await http.get('/permissions/')
    permissions.value = data.results || data
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  } finally {
    loading.permissions = false
  }
}

// 获取用户角色关联列表
const fetchUserRoles = async () => {
  loading.userRoles = true
  try {
    const { data } = await http.get('/user-roles/')
    // 后端直接返回 user_username 和 role_name 字段
    userRoles.value = data.results || data
  } catch (error) {
    ElMessage.error('获取用户角色列表失败')
  } finally {
    loading.userRoles = false
  }
}

// 获取角色权限关联列表
const fetchRolePermissions = async () => {
  loading.rolePermissions = true
  try {
    const { data } = await http.get('/role-permissions/')
    // 后端直接返回 role_name 和 permission_name 字段
    rolePermissions.value = data.results || data
  } catch (error) {
    ElMessage.error('获取角色权限列表失败')
  } finally {
    loading.rolePermissions = false
  }
}

// 获取用户列表
const fetchUsers = async () => {
  try {
    const { data } = await http.get('/users/')
    users.value = data.results || data
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
}

// 打开角色对话框
const openRoleDialog = (role = null) => {
  if (role) {
    Object.assign(roleForm, role)
  } else {
    Object.assign(roleForm, { id: null, name: '', description: '' })
  }
  roleDialogVisible.value = true
}

// 打开权限对话框
const openPermissionDialog = (permission = null) => {
  if (permission) {
    Object.assign(permissionForm, permission)
  } else {
    Object.assign(permissionForm, { id: null, name: '', codename: '', description: '' })
  }
  permissionDialogVisible.value = true
}

// 打开用户角色对话框
const openUserRoleDialog = (userRole = null) => {
  if (userRole) {
    Object.assign(userRoleForm, userRole)
  } else {
    Object.assign(userRoleForm, { id: null, user: null, role: null })
  }
  userRoleDialogVisible.value = true
}

// 打开角色权限对话框
const openRolePermissionDialog = (rolePermission = null) => {
  if (rolePermission) {
    Object.assign(rolePermissionForm, rolePermission)
  } else {
    Object.assign(rolePermissionForm, { id: null, role: null, permission: null })
  }
  rolePermissionDialogVisible.value = true
}

// 保存角色
const saveRole = async () => {
  const valid = await roleFormRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    if (roleForm.id) {
      await http.put(`/roles/${roleForm.id}/`, roleForm)
      ElMessage.success('角色更新成功')
    } else {
      await http.post('/roles/', roleForm)
      ElMessage.success('角色创建成功')
    }
    roleDialogVisible.value = false
    fetchRoles()
  } catch (error) {
    ElMessage.error('保存角色失败')
  }
}

// 保存权限
const savePermission = async () => {
  const valid = await permissionFormRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    if (permissionForm.id) {
      await http.put(`/permissions/${permissionForm.id}/`, permissionForm)
      ElMessage.success('权限更新成功')
    } else {
      await http.post('/permissions/', permissionForm)
      ElMessage.success('权限创建成功')
    }
    permissionDialogVisible.value = false
    fetchPermissions()
  } catch (error) {
    ElMessage.error('保存权限失败')
  }
}

// 保存用户角色
const saveUserRole = async () => {
  const valid = await userRoleFormRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    if (userRoleForm.id) {
      await http.put(`/user-roles/${userRoleForm.id}/`, userRoleForm)
      ElMessage.success('用户角色更新成功')
    } else {
      await http.post('/user-roles/', userRoleForm)
      ElMessage.success('用户角色分配成功')
    }
    userRoleDialogVisible.value = false
    fetchUserRoles()
  } catch (error) {
    ElMessage.error('保存用户角色失败')
  }
}

// 保存角色权限
const saveRolePermission = async () => {
  const valid = await rolePermissionFormRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    if (rolePermissionForm.id) {
      await http.put(`/role-permissions/${rolePermissionForm.id}/`, rolePermissionForm)
      ElMessage.success('角色权限更新成功')
    } else {
      await http.post('/role-permissions/', rolePermissionForm)
      ElMessage.success('角色权限分配成功')
    }
    rolePermissionDialogVisible.value = false
    fetchRolePermissions()
  } catch (error) {
    ElMessage.error('保存角色权限失败')
  }
}

// 删除角色
const deleteRole = (role) => {
  ElMessageBox.confirm(`确定要删除角色 "${role.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await http.delete(`/roles/${role.id}/`)
      ElMessage.success('角色删除成功')
      fetchRoles()
    } catch (error) {
      ElMessage.error('删除角色失败')
    }
  }).catch(() => {})
}

// 删除权限
const deletePermission = (permission) => {
  ElMessageBox.confirm(`确定要删除权限 "${permission.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await http.delete(`/permissions/${permission.id}/`)
      ElMessage.success('权限删除成功')
      fetchPermissions()
    } catch (error) {
      ElMessage.error('删除权限失败')
    }
  }).catch(() => {})
}

// 删除用户角色
const deleteUserRole = (userRole) => {
  ElMessageBox.confirm(`确定要移除该用户角色吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await http.delete(`/user-roles/${userRole.id}/`)
      ElMessage.success('用户角色移除成功')
      fetchUserRoles()
    } catch (error) {
      ElMessage.error('移除用户角色失败')
    }
  }).catch(() => {})
}

// 删除角色权限
const deleteRolePermission = (rolePermission) => {
  ElMessageBox.confirm(`确定要移除该角色权限吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await http.delete(`/role-permissions/${rolePermission.id}/`)
      ElMessage.success('角色权限移除成功')
      fetchRolePermissions()
    } catch (error) {
      ElMessage.error('移除角色权限失败')
    }
  }).catch(() => {})
}

// 组件挂载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.role-permission-container {
  padding: 20px;
}

.role-permission-tabs {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  background-color: white;
  padding: 20px;
}

.tab-content {
  padding: 20px 0;
}

.toolbar {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
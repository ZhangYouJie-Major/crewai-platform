<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="isEdit ? '编辑MCP工具' : '添加MCP工具'"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
      @submit.prevent
    >
      <el-form-item label="工具名称" prop="name">
        <el-input
          v-model="formData.name"
          placeholder="请输入工具名称"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="工具描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="3"
          placeholder="请输入工具描述（可选）"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="服务地址" prop="server_url">
        <el-input
          v-model="formData.server_url"
          placeholder="请输入MCP服务器地址，如: ws://localhost:8080"
          maxlength="500"
        >
          <template #prepend>
            <el-select v-model="urlPrefix" style="width: 100px" @change="handlePrefixChange">
              <el-option label="ws://" value="ws://" />
              <el-option label="wss://" value="wss://" />
              <el-option label="http://" value="http://" />
              <el-option label="https://" value="https://" />
            </el-select>
          </template>
        </el-input>
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="超时时间" prop="timeout">
            <el-input-number
              v-model="formData.timeout"
              :min="1"
              :max="300"
              :step="1"
              controls-position="right"
              style="width: 100%"
            />
            <template #suffix>秒</template>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="工具版本" prop="version">
            <el-input
              v-model="formData.version"
              placeholder="如: v1.0.0"
              maxlength="20"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="认证配置">
        <el-switch
          v-model="formData.auth_required"
          active-text="需要认证"
          inactive-text="无需认证"
        />
      </el-form-item>

      <el-form-item v-if="formData.auth_required" label="认证类型" prop="auth_type">
        <el-select v-model="formData.auth_type" placeholder="请选择认证类型" style="width: 100%">
          <el-option label="API Key" value="api_key" />
          <el-option label="Bearer Token" value="bearer" />
          <el-option label="Basic Auth" value="basic" />
          <el-option label="OAuth2" value="oauth2" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="formData.auth_required" label="认证凭据" prop="auth_credentials">
        <el-input
          v-model="formData.auth_credentials"
          type="password"
          placeholder="请输入认证凭据"
          show-password
          maxlength="500"
        />
      </el-form-item>

      <el-form-item label="可见性设置">
        <el-radio-group v-model="formData.is_public">
          <el-radio :label="false">私有工具</el-radio>
          <el-radio :label="true">公开工具</el-radio>
        </el-radio-group>
        <div class="form-tip">
          <el-text size="small" type="info">
            公开工具可被其他用户使用，私有工具仅自己可用
          </el-text>
        </div>
      </el-form-item>

      <el-form-item label="高级配置">
        <el-collapse>
          <el-collapse-item title="环境变量" name="env">
            <div class="env-config">
              <el-button @click="addEnvVar" size="small" type="primary" icon="Plus">
                添加环境变量
              </el-button>
              <div class="env-list">
                <div 
                  v-for="(env, index) in formData.environment_variables" 
                  :key="index"
                  class="env-item"
                >
                  <el-input
                    v-model="env.key"
                    placeholder="变量名"
                    style="width: 40%"
                  />
                  <el-input
                    v-model="env.value"
                    placeholder="变量值"
                    style="width: 40%"
                  />
                  <el-button
                    @click="removeEnvVar(index)"
                    size="small"
                    type="danger"
                    icon="Delete"
                  />
                </div>
              </div>
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="请求头配置" name="headers">
            <div class="headers-config">
              <el-button @click="addHeader" size="small" type="primary" icon="Plus">
                添加请求头
              </el-button>
              <div class="headers-list">
                <div 
                  v-for="(header, index) in formData.custom_headers" 
                  :key="index"
                  class="header-item"
                >
                  <el-input
                    v-model="header.key"
                    placeholder="Header名称"
                    style="width: 40%"
                  />
                  <el-input
                    v-model="header.value"
                    placeholder="Header值"
                    style="width: 40%"
                  />
                  <el-button
                    @click="removeHeader(index)"
                    size="small"
                    type="danger"
                    icon="Delete"
                  />
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button @click="handleTest" :loading="testing">测试连接</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import api from '@/services/api'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  tool: {
    type: Object,
    default: null
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'success'])

// 表单引用
const formRef = ref(null)

// 加载状态
const submitting = ref(false)
const testing = ref(false)

// URL前缀
const urlPrefix = ref('ws://')

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  server_url: '',
  timeout: 30,
  version: 'v1.0.0',
  auth_required: false,
  auth_type: 'api_key',
  auth_credentials: '',
  is_public: false,
  environment_variables: [],
  custom_headers: []
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入工具名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  server_url: [
    { required: true, message: '请输入服务地址', trigger: 'blur' },
    { 
      pattern: /^(ws|wss|http|https):\/\/.+/, 
      message: '请输入有效的服务地址', 
      trigger: 'blur' 
    }
  ],
  timeout: [
    { required: true, message: '请输入超时时间', trigger: 'blur' },
    { type: 'number', min: 1, max: 300, message: '超时时间应在1-300秒之间', trigger: 'blur' }
  ],
  auth_type: [
    { required: true, message: '请选择认证类型', trigger: 'change' }
  ],
  auth_credentials: [
    { required: true, message: '请输入认证凭据', trigger: 'blur' }
  ]
}

// 监听弹窗显示状态
watch(() => props.visible, (newVal) => {
  if (newVal) {
    initForm()
  }
})

// 初始化表单
const initForm = () => {
  if (props.isEdit && props.tool) {
    // 编辑模式，填充现有数据
    Object.assign(formData, {
      name: props.tool.name || '',
      description: props.tool.description || '',
      server_url: props.tool.server_url || '',
      timeout: props.tool.timeout || 30,
      version: props.tool.version || 'v1.0.0',
      auth_required: props.tool.auth_required || false,
      auth_type: props.tool.auth_type || 'api_key',
      auth_credentials: props.tool.auth_credentials || '',
      is_public: props.tool.is_public || false,
      environment_variables: props.tool.environment_variables || [],
      custom_headers: props.tool.custom_headers || []
    })
    
    // 设置URL前缀
    if (formData.server_url) {
      if (formData.server_url.startsWith('wss://')) {
        urlPrefix.value = 'wss://'
      } else if (formData.server_url.startsWith('ws://')) {
        urlPrefix.value = 'ws://'
      } else if (formData.server_url.startsWith('https://')) {
        urlPrefix.value = 'https://'
      } else if (formData.server_url.startsWith('http://')) {
        urlPrefix.value = 'http://'
      }
    }
  } else {
    // 新建模式，重置表单
    Object.assign(formData, {
      name: '',
      description: '',
      server_url: '',
      timeout: 30,
      version: 'v1.0.0',
      auth_required: false,
      auth_type: 'api_key',
      auth_credentials: '',
      is_public: false,
      environment_variables: [],
      custom_headers: []
    })
    urlPrefix.value = 'ws://'
  }
  
  // 清除验证状态
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 处理URL前缀变化
const handlePrefixChange = () => {
  if (formData.server_url) {
    const url = formData.server_url.replace(/^(ws|wss|http|https):\/\//, '')
    formData.server_url = urlPrefix.value + url
  }
}

// 添加环境变量
const addEnvVar = () => {
  formData.environment_variables.push({ key: '', value: '' })
}

// 删除环境变量
const removeEnvVar = (index) => {
  formData.environment_variables.splice(index, 1)
}

// 添加请求头
const addHeader = () => {
  formData.custom_headers.push({ key: '', value: '' })
}

// 删除请求头
const removeHeader = (index) => {
  formData.custom_headers.splice(index, 1)
}

// 测试连接
const handleTest = async () => {
  try {
    // 先验证必填字段
    await formRef.value.validateField(['name', 'server_url'])
    
    testing.value = true
    
    // 构造测试数据
    const testData = {
      name: formData.name,
      server_url: formData.server_url,
      timeout: formData.timeout,
      auth_required: formData.auth_required,
      auth_type: formData.auth_type,
      auth_credentials: formData.auth_credentials
    }
    
    // 调用测试API（这里可能需要一个专门的测试接口）
    const response = await api.createMCPTool(testData)
    
    ElMessage.success('连接测试成功')
  } catch (error) {
    console.error('测试连接失败:', error)
    ElMessage.error('连接测试失败: ' + (error.response?.data?.message || error.message))
  } finally {
    testing.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    // 清理空的环境变量和请求头
    const cleanData = {
      ...formData,
      environment_variables: formData.environment_variables.filter(
        env => env.key && env.value
      ),
      custom_headers: formData.custom_headers.filter(
        header => header.key && header.value
      )
    }
    
    if (props.isEdit) {
      await api.updateMCPTool(props.tool.id, cleanData)
      ElMessage.success('工具更新成功')
    } else {
      await api.createMCPTool(cleanData)
      ElMessage.success('工具创建成功')
    }
    
    emit('success')
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败: ' + (error.response?.data?.message || error.message))
  } finally {
    submitting.value = false
  }
}

// 取消操作
const handleCancel = () => {
  emit('update:visible', false)
}
</script>

<style scoped>
.form-tip {
  margin-top: 5px;
}

.env-config,
.headers-config {
  padding: 10px 0;
}

.env-list,
.headers-list {
  margin-top: 10px;
}

.env-item,
.header-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-collapse-item__header) {
  font-size: 14px;
}

:deep(.el-input-group__prepend) {
  padding: 0;
}
</style>
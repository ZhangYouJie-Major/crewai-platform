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
          placeholder="请输入工具名称（唯一标识）"
          maxlength="64"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="显示名称" prop="display_name">
        <el-input
          v-model="formData.display_name"
          placeholder="请输入显示名称（用于界面展示）"
          maxlength="128"
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

      <el-form-item label="服务器类型" prop="server_type">
        <el-select v-model="formData.server_type" placeholder="请选择服务器类型" style="width: 100%">
          <el-option label="SSE (Server-Sent Events)" value="sse" />
          <el-option label="HTTP (标准HTTP)" value="http" />
          <el-option label="STDIO (标准输入输出)" value="stdio" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="formData.server_type === 'sse' || formData.server_type === 'http'" label="服务地址" prop="server_url">
        <el-input
          v-model="connectionConfig.url"
          placeholder="请输入服务器地址，如: https://api.example.com"
          maxlength="500"
        />
      </el-form-item>

      <el-form-item v-if="formData.server_type === 'stdio'" label="命令配置">
        <el-row :gutter="10">
          <el-col :span="12">
            <el-input
              v-model="connectionConfig.command"
              placeholder="命令，如: npx"
            />
          </el-col>
          <el-col :span="12">
            <el-input
              v-model="argsString"
              placeholder="参数，用空格分隔"
            />
          </el-col>
        </el-row>
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="连接超时" prop="connection_timeout">
            <el-input-number
              v-model="formData.connection_timeout"
              :min="1"
              :max="300"
              :step="1"
              controls-position="right"
              style="width: 100%"
            />
            <span style="margin-left: 8px; color: #999;">秒</span>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="工具版本" prop="version">
            <el-input
              v-model="formData.version"
              placeholder="如: v1.0.0"
              maxlength="32"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="认证配置">
        <el-switch
          v-model="needAuth"
          active-text="需要认证"
          inactive-text="无需认证"
        />
      </el-form-item>

      <el-form-item v-if="needAuth" label="Authorization">
        <el-input
          v-model="authToken"
          type="password"
          placeholder="请输入API Key或Token"
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

// 认证相关
const needAuth = ref(false)
const authToken = ref('')
const argsString = ref('')

// 连接配置
const connectionConfig = reactive({
  url: '',
  command: '',
  args: [],
  headers: {}
})

// 表单数据
const formData = reactive({
  name: '',
  display_name: '',
  description: '',
  server_type: '',
  connection_config: {},
  connection_timeout: 30,
  version: '',
  is_public: false
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入工具名称', trigger: 'blur' },
    { min: 2, max: 64, message: '长度在 2 到 64 个字符', trigger: 'blur' }
  ],
  display_name: [
    { required: true, message: '请输入显示名称', trigger: 'blur' },
    { min: 2, max: 128, message: '长度在 2 到 128 个字符', trigger: 'blur' }
  ],
  server_type: [
    { required: true, message: '请选择服务器类型', trigger: 'change' }
  ],
  connection_timeout: [
    { required: true, message: '请输入连接超时时间', trigger: 'blur' },
    { type: 'number', min: 1, max: 300, message: '超时时间应在1-300秒之间', trigger: 'blur' }
  ]
}

// 监听弹窗显示状态
watch(() => props.visible, (newVal) => {
  if (newVal) {
    initForm()
  }
})

// 监听参数字符串变化
watch(argsString, (newVal) => {
  connectionConfig.args = newVal ? newVal.split(' ').filter(arg => arg.trim()) : []
})

// 监听认证配置变化
watch(needAuth, (newVal) => {
  if (newVal && authToken.value) {
    connectionConfig.headers = {
      ...connectionConfig.headers,
      Authorization: `Bearer ${authToken.value}`
    }
  } else {
    delete connectionConfig.headers.Authorization
  }
})

watch(authToken, (newVal) => {
  if (needAuth.value && newVal) {
    connectionConfig.headers = {
      ...connectionConfig.headers,
      Authorization: `Bearer ${newVal}`
    }
  } else {
    delete connectionConfig.headers.Authorization
  }
})

// 初始化表单
const initForm = () => {
  if (props.isEdit && props.tool) {
    // 编辑模式，填充现有数据
    Object.assign(formData, {
      name: props.tool.name || '',
      display_name: props.tool.display_name || '',
      description: props.tool.description || '',
      server_type: props.tool.server_type || '',
      connection_timeout: props.tool.connection_timeout || 30,
      version: props.tool.version || '',
      is_public: props.tool.is_public || false
    })
    
    // 解析连接配置
    const config = props.tool.connection_config || {}
    Object.assign(connectionConfig, {
      url: config.url || '',
      command: config.command || '',
      args: config.args || [],
      headers: config.headers || {}
    })
    
    // 设置UI状态
    argsString.value = connectionConfig.args.join(' ')
    const authHeader = connectionConfig.headers.Authorization
    if (authHeader) {
      needAuth.value = true
      authToken.value = authHeader.replace('Bearer ', '')
    }
  } else {
    // 新建模式，重置表单
    Object.assign(formData, {
      name: '',
      display_name: '',
      description: '',
      server_type: 'sse',
      connection_timeout: 30,
      version: 'v1.0.0',
      is_public: false
    })
    
    Object.assign(connectionConfig, {
      url: '',
      command: '',
      args: [],
      headers: {}
    })
    
    needAuth.value = false
    authToken.value = ''
    argsString.value = ''
  }
  
  // 清除验证状态
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 构建连接配置
const buildConnectionConfig = () => {
  const config = { ...connectionConfig }
  
  // 清理空值
  if (!config.url) delete config.url
  if (!config.command) delete config.command
  if (!config.args || config.args.length === 0) delete config.args
  if (!config.headers || Object.keys(config.headers).length === 0) delete config.headers
  
  return config
}

// 测试连接
const handleTest = async () => {
  try {
    // 如果是编辑模式且有工具ID，直接调用健康检查API
    if (props.isEdit && props.tool?.id) {
      testing.value = true
      const response = await api.healthCheckMCPTool(props.tool.id)
      
      if (response.data.success) {
        ElMessage.success('工具健康检查通过')
      } else {
        ElMessage.warning(`工具健康检查失败: ${response.data.message}`)
      }
    } else {
      // 新建模式，先验证必填字段
      await formRef.value.validateField(['name', 'display_name', 'server_type'])
      
      testing.value = true
      
      // 构造测试数据
      const testData = {
        ...formData,
        connection_config: buildConnectionConfig()
      }
      
      // 新建模式下，可以先创建临时工具进行测试，或者提示用户先保存
      ElMessage.info('请先创建工具后再进行连接测试')
    }
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
    
    // 构建提交数据
    const submitData = {
      ...formData,
      connection_config: buildConnectionConfig()
    }
    
    if (props.isEdit) {
      await api.updateMCPTool(props.tool.id, submitData)
      ElMessage.success('工具更新成功')
    } else {
      await api.createMCPTool(submitData)
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
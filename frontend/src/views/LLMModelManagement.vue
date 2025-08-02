<template>
  <div class="llm-model-management">
    <div class="page-header">
      <h1>LLM模型配置管理</h1>
      <p>配置和管理AI大语言模型，支持多种提供商的API集成</p>
    </div>

    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button
        type="primary"
        icon="Plus"
        @click="showCreateDialog"
      >
        添加模型
      </el-button>
      
      <el-button
        type="warning"
        icon="Refresh"
        @click="batchValidateModels"
        :loading="batchValidating"
      >
        批量验证
      </el-button>
      
      <div class="search-box">
        <el-input
          v-model="searchText"
          placeholder="搜索模型名称或提供商"
          prefix-icon="Search"
          clearable
          @input="handleSearch"
        />
      </div>
    </div>

    <!-- 模型列表 -->
    <el-table
      :data="filteredModels"
      v-loading="loading"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="name" label="模型名称" width="180">
        <template #default="scope">
          <div class="model-name">
            <el-tag
              :type="scope.row.is_available ? 'success' : 'danger'"
              size="small"
              round
            >
              {{ scope.row.is_available ? '可用' : '不可用' }}
            </el-tag>
            <span>{{ scope.row.name }}</span>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="provider" label="提供商" width="120">
        <template #default="scope">
          <el-tag :type="getProviderTagType(scope.row.provider)">
            {{ getProviderDisplay(scope.row.provider) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="model_name" label="模型标识" width="200" />
      
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      
      <el-table-column prop="last_validated" label="最后验证" width="160">
        <template #default="scope">
          <span v-if="scope.row.last_validated">
            {{ formatDateTime(scope.row.last_validated) }}
          </span>
          <span v-else class="text-muted">未验证</span>
        </template>
      </el-table-column>
      
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="scope">
          <el-switch
            v-model="scope.row.is_active"
            @change="handleStatusChange(scope.row)"
          />
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="scope">
          <el-button
            type="success"
            size="small"
            icon="Connection"
            @click="validateModel(scope.row)"
            :loading="scope.row.validating"
          >
            验证连接
          </el-button>
          
          <el-button
            type="primary"
            size="small"
            icon="List"
            @click="getModelsList(scope.row)"
            :loading="scope.row.fetchingModels"
          >
            获取模型
          </el-button>
          
          <el-button
            type="warning"
            size="small"
            icon="Edit"
            @click="editModel(scope.row)"
          >
            编辑
          </el-button>
          
          <el-button
            type="danger"
            size="small"
            icon="Delete"
            @click="deleteModel(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑LLM模型' : '创建LLM模型'"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模型名称" prop="name">
              <el-input
                v-model="formData.name"
                placeholder="请输入模型显示名称"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="提供商" prop="provider">
              <el-select
                v-model="formData.provider"
                placeholder="选择AI提供商"
                :loading="providersLoading"
                @change="handleProviderChange"
              >
                <el-option
                  v-for="provider in providers"
                  :key="provider.value"
                  :label="provider.label"
                  :value="provider.value"
                />
              </el-select>
              <div style="font-size: 12px; color: #666; margin-top: 4px;">
                选择提供商后，模型标识下拉框会自动显示该提供商的常用模型选项
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模型标识" prop="model_name">
              <el-select
                v-model="formData.model_name"
                placeholder="选择或输入模型名称"
                filterable
                allow-create
                :loading="fetchingAvailableModels"
              >
                <el-option
                  v-for="model in availableModels"
                  :key="model"
                  :label="model"
                  :value="model"
                />
              </el-select>
              <div style="font-size: 12px; color: #666; margin-top: 4px;">
                模型的具体标识符，如 gpt-4、claude-3-sonnet、moonshot-v1-8k 等。
                <br>选择提供商后会显示常用模型，也可以手动输入或测试连接后获取。
              </div>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="API基础URL" prop="api_base_url">
              <el-input
                v-model="formData.api_base_url"
                placeholder="自定义API端点（可选）"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="API密钥" prop="api_key">
          <el-input
            v-model="formData.api_key"
            type="password"
            placeholder="请输入API密钥"
            show-password
          />
        </el-form-item>

        <el-row :gutter="20" v-if="formData.provider === 'azure_openai'">
          <el-col :span="12">
            <el-form-item label="API版本" prop="api_version">
              <el-input
                v-model="formData.api_version"
                placeholder="如：2024-02-01"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="温度参数" prop="temperature">
              <el-slider
                v-model="formData.temperature"
                :min="0"
                :max="2"
                :step="0.1"
                show-input
                :show-input-controls="false"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="最大Token" prop="max_tokens">
              <el-input-number
                v-model="formData.max_tokens"
                :min="1"
                :max="100000"
                placeholder="可选"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="超时时间(秒)" prop="timeout">
              <el-input-number
                v-model="formData.timeout"
                :min="1"
                :max="300"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="模型描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="模型的详细描述（可选）"
          />
        </el-form-item>

        <!-- 连接测试区域 -->
        <el-divider content-position="left">连接测试</el-divider>
        
        <div class="test-section">
          <el-button
            type="primary"
            @click="testConnection"
            :loading="testing"
            :disabled="!canTest"
          >
            测试连接并获取模型列表
          </el-button>
          
          <div v-if="!canTest" style="margin-top: 8px;">
            <el-text type="info" size="small">
              请先配置供应商、模型标识和API密钥后再进行测试
            </el-text>
          </div>
          
          <div v-if="testResult" class="test-result">
            <el-alert
              :type="testResult.success ? 'success' : 'error'"
              :title="testResult.success ? '连接成功' : '连接失败'"
              :description="testResult.message"
              show-icon
              :closable="false"
            />
            
            <!-- 显示获取到的模型列表 -->
            <div v-if="testResult.success && testResult.models && testResult.models.length > 0" class="models-list">
              <h4>可用模型列表：</h4>
              <el-tag
                v-for="model in testResult.models"
                :key="model"
                @click="formData.model_name = model"
                style="margin: 2px; cursor: pointer;"
              >
                {{ model }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="handleSubmit"
            :loading="submitting"
          >
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 模型列表对话框 -->
    <el-dialog
      v-model="modelsDialogVisible"
      title="可用模型列表"
      width="600px"
    >
      <div v-if="selectedModelsList.length > 0">
        <p>从 <strong>{{ selectedModelInfo.name }}</strong> 获取到以下模型：</p>
        <el-tag
          v-for="model in selectedModelsList"
          :key="model"
          style="margin: 4px;"
        >
          {{ model }}
        </el-tag>
      </div>
      <div v-else>
        <el-empty description="暂无可用模型" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/services/api'

// 响应式数据
const loading = ref(false)
const models = ref([])
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 对话框状态
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const submitting = ref(false)
const testing = ref(false)
const testResult = ref(null)
const batchValidating = ref(false)

// 模型列表对话框
const modelsDialogVisible = ref(false)
const selectedModelsList = ref([])
const selectedModelInfo = ref({})
const fetchingAvailableModels = ref(false)
const availableModels = ref([])

// 表单数据
const formData = reactive({
  name: '',
  provider: 'openai',
  model_name: '',
  description: '',
  api_base_url: '',
  api_key: '',
  api_version: '',
  temperature: 0.7,
  max_tokens: null,
  timeout: 30,
  max_retries: 2,
  is_active: true
})

// 提供商选项 - 从字典API获取
const providers = ref([])
const providersLoading = ref(false)

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  provider: [
    { required: true, message: '请选择提供商', trigger: 'change' }
  ],
  model_name: [
    { required: true, message: '请输入模型标识', trigger: 'blur' }
  ],
  api_key: [
    { required: true, message: '请输入API密钥', trigger: 'blur' }
  ],
  temperature: [
    { type: 'number', min: 0, max: 2, message: '温度参数必须在0-2之间', trigger: 'change' }
  ],
  timeout: [
    { type: 'number', min: 1, max: 300, message: '超时时间必须在1-300秒之间', trigger: 'change' }
  ]
}

// 计算属性
const filteredModels = computed(() => {
  if (!searchText.value) return models.value
  
  const search = searchText.value.toLowerCase()
  return models.value.filter(model => 
    model.name.toLowerCase().includes(search) ||
    model.provider.toLowerCase().includes(search) ||
    model.model_name.toLowerCase().includes(search)
  )
})

const canTest = computed(() => {
  return formData.provider && formData.model_name && formData.api_key && 
         (formData.provider !== 'azure_openai' || formData.api_base_url)
})

// 方法
const loadModels = async () => {
  loading.value = true
  try {
    const response = await api.getLLMModels({
      page: currentPage.value,
      page_size: pageSize.value
    })
    
    models.value = response.data.results || response.data || []
    total.value = response.data.count || models.value.length
  } catch (error) {
    ElMessage.error('加载模型列表失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  resetFormData()
  testResult.value = null
  dialogVisible.value = true
}

// 加载提供商列表
const loadProviders = async () => {
  try {
    providersLoading.value = true
    // 获取LLM供应商字典选项
    const response = await api.getDictionaryOptions({ code: 'llm_provider' })
    
    // 转换数据格式为下拉选项格式
    providers.value = response.data.items.map(item => ({
      value: item.code,
      label: item.name
    }))
  } catch (error) {
    console.error('加载提供商列表失败:', error)
    ElMessage.error('加载提供商列表失败')
    // 如果API失败，使用默认的提供商列表作为后备
    providers.value = [
      { value: 'openai', label: 'OpenAI' },
      { value: 'google', label: 'Google' },
      { value: 'anthropic', label: 'Anthropic' },
      { value: 'baidu', label: '百度' },
      { value: 'alibaba', label: '阿里云' },
      { value: 'tencent', label: '腾讯' },
      { value: 'zhipu', label: '智谱AI' },
      { value: 'moonshot', label: 'Moonshot' }
    ]
  } finally {
    providersLoading.value = false
  }
}

const editModel = (model) => {
  isEdit.value = true
  Object.assign(formData, {
    ...model,
    api_key: '' // 编辑时不显示原密钥
  })
  testResult.value = null
  dialogVisible.value = true
}

const resetFormData = () => {
  Object.assign(formData, {
    name: '',
    provider: '', // 改为空字符串，等待提供商列表加载完成后设置
    model_name: '',
    description: '',
    api_base_url: '',
    api_key: '',
    api_version: '',
    temperature: 0.7,
    max_tokens: null,
    timeout: 30,
    max_retries: 2,
    is_active: true
  })
  availableModels.value = []
}

const handleProviderChange = async (provider) => {
  // 重置相关字段
  formData.model_name = ''
  formData.api_base_url = ''
  formData.api_version = ''
  
  if (!provider) {
    availableModels.value = []
    return
  }
  
  try {
    fetchingAvailableModels.value = true
    
    // 从字典API获取该供应商下的模型选项
    const response = await api.getDictionaryOptions({ 
      code: 'llm_provider',
      parent_code: provider
    })
    
    // 转换数据格式为模型代码数组
    availableModels.value = response.data.items.map(item => item.code)
    
    // 设置特定供应商的默认配置
    if (provider === 'azure_openai') {
      formData.api_version = '2024-02-01'
    } else if (provider === 'ollama') {
      formData.api_base_url = 'http://localhost:11434'
    }
    
  } catch (error) {
    console.error('获取模型列表失败:', error)
    // 如果API失败，使用默认的模型列表作为后备
    setFallbackModels(provider)
  } finally {
    fetchingAvailableModels.value = false
  }
}

// 后备模型列表方法
const setFallbackModels = (provider) => {
  const fallbackModels = {
    'openai': ['gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
    'google': ['gemini-pro', 'gemini-1.5-pro', 'gemini-ultra', 'gemini-nano'],
    'anthropic': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku', 'claude-2'],
    'baidu': ['ernie-bot', 'ernie-bot-turbo', 'ernie-bot-4', 'ernie-3.5'],
    'alibaba': ['qwen-max', 'qwen-plus', 'qwen-turbo', 'qwen-7b'],
    'tencent': ['hunyuan-pro', 'hunyuan-standard', 'hunyuan-lite'],
    'zhipu': ['glm-4', 'glm-3-turbo', 'chatglm-6b'],
    'moonshot': ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k']
  }
  
  availableModels.value = fallbackModels[provider] || []
}

const testConnection = async () => {
  testing.value = true
  testResult.value = null
  
  try {
    // 构建测试数据
    const testData = {
      provider: formData.provider,
      api_key: formData.api_key,
      api_base_url: formData.api_base_url,
      api_version: formData.api_version,
      model_name: formData.model_name || 'test'
    }
    
    // 调用测试API
    const response = await api.testLLMModelConnection(testData)
    
    testResult.value = {
      success: true,
      message: '连接成功！',
      models: response.data.available_models || []
    }
    
    // 更新可用模型列表
    if (response.data.available_models) {
      availableModels.value = response.data.available_models
    }
    
    ElMessage.success('连接测试成功')
  } catch (error) {
    testResult.value = {
      success: false,
      message: error.response?.data?.error || error.message
    }
    ElMessage.error('连接测试失败')
  } finally {
    testing.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    const submitData = { ...formData }
    
    // 清理空值
    Object.keys(submitData).forEach(key => {
      if (submitData[key] === '' || submitData[key] === null) {
        delete submitData[key]
      }
    })
    
    if (isEdit.value) {
      await api.updateLLMModel(formData.id, submitData)
      ElMessage.success('模型更新成功')
    } else {
      await api.createLLMModel(submitData)
      ElMessage.success('模型创建成功')
    }
    
    dialogVisible.value = false
    loadModels()
  } catch (error) {
    ElMessage.error('操作失败：' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

const validateModel = async (model) => {
  model.validating = true
  try {
    const response = await api.validateLLMModelConnection(model.id)
    
    if (response.data.success) {
      ElMessage.success('模型验证成功')
      model.is_available = true
      model.last_validated = new Date().toISOString()
    } else {
      ElMessage.error('模型验证失败：' + response.data.message)
      model.is_available = false
    }
  } catch (error) {
    ElMessage.error('验证请求失败：' + error.message)
  } finally {
    model.validating = false
  }
}

const getModelsList = async (model) => {
  model.fetchingModels = true
  try {
    const response = await api.getLLMModelModels(model.id)
    
    selectedModelInfo.value = model
    selectedModelsList.value = response.data.models || []
    modelsDialogVisible.value = true
    
    if (selectedModelsList.value.length === 0) {
      ElMessage.warning('未获取到可用模型列表')
    }
  } catch (error) {
    ElMessage.error('获取模型列表失败：' + error.message)
  } finally {
    model.fetchingModels = false
  }
}

const deleteModel = async (model) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型 "${model.name}" 吗？此操作不可撤销。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await api.deleteLLMModel(model.id)
    ElMessage.success('模型删除成功')
    loadModels()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

const handleStatusChange = async (model) => {
  try {
    await api.patchLLMModel(model.id, {
      is_active: model.is_active
    })
    ElMessage.success(`模型已${model.is_active ? '启用' : '禁用'}`)
  } catch (error) {
    // 回滚状态
    model.is_active = !model.is_active
    ElMessage.error('状态更新失败：' + error.message)
  }
}

const batchValidateModels = async () => {
  batchValidating.value = true
  try {
    const response = await api.batchValidateLLMModels()
    
    ElMessage.success(`批量验证完成：${response.data.available}/${response.data.total} 个模型可用`)
    loadModels()
  } catch (error) {
    ElMessage.error('批量验证失败：' + error.message)
  } finally {
    batchValidating.value = false
  }
}

const handleSearch = () => {
  // 搜索逻辑已在computed中实现
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadModels()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadModels()
}

const getProviderDisplay = (provider) => {
  const providerMap = {
    'openai': 'OpenAI',
    'anthropic': 'Anthropic',
    'azure_openai': 'Azure',
    'ollama': 'Ollama',
    'huggingface': 'HuggingFace',
    'google': 'Google',
    'cohere': 'Cohere',
    'custom': '自定义'
  }
  return providerMap[provider] || provider
}

const getProviderTagType = (provider) => {
  const typeMap = {
    'openai': 'primary',
    'anthropic': 'success',
    'azure_openai': 'info',
    'ollama': 'warning',
    'huggingface': '',
    'google': 'danger',
    'cohere': '',
    'custom': 'info'
  }
  return typeMap[provider] || ''
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 生命周期
onMounted(async () => {
  // 并行加载模型列表和提供商列表
  await Promise.all([
    loadModels(),
    loadProviders()
  ])
  
  // 设置默认提供商（取第一个提供商作为默认值）
  if (providers.value.length > 0 && !formData.provider) {
    formData.provider = providers.value[0].value
    await handleProviderChange(formData.provider)
  }
})
</script>

<style scoped>
.llm-model-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.search-box {
  margin-left: auto;
  width: 300px;
}

.model-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.text-muted {
  color: #999;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.test-section {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.test-result {
  margin-top: 16px;
}

.models-list {
  margin-top: 16px;
  padding: 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e6e6e6;
}

.models-list h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #333;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
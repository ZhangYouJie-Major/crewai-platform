<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑Agent' : '创建Agent'"
    width="900px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @closed="handleClosed"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      label-position="left"
      class="agent-form"
    >
      <el-tabs v-model="activeTab" class="config-tabs">
        <!-- 基本配置 -->
        <el-tab-pane label="基本信息" name="basic">
          <div class="form-section">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Agent名称" prop="name">
                  <el-input 
                    v-model="form.name" 
                    placeholder="输入Agent的唯一标识名称"
                    :disabled="isEdit"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="显示名称" prop="display_name">
                  <el-input 
                    v-model="form.display_name" 
                    placeholder="输入友好的显示名称"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="Agent描述" prop="description">
              <el-input 
                v-model="form.description" 
                type="textarea" 
                :rows="3"
                placeholder="描述Agent的功能和用途"
              />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="角色定义" prop="role">
                  <el-input 
                    v-model="form.role" 
                    placeholder="如：数据分析师、文档编写员"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="是否公开">
                  <el-switch 
                    v-model="form.is_public"
                    active-text="公开"
                    inactive-text="私有"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="是否启用">
                  <el-switch 
                    v-model="form.is_active"
                    active-text="启用"
                    inactive-text="禁用"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="目标描述" prop="goal">
              <el-input 
                v-model="form.goal" 
                type="textarea" 
                :rows="3"
                placeholder="描述Agent的主要目标和职责"
              />
            </el-form-item>

            <el-form-item label="背景故事" prop="backstory">
              <el-input 
                v-model="form.backstory" 
                type="textarea" 
                :rows="4"
                placeholder="描述Agent的背景故事，增强其人格化特征"
              />
            </el-form-item>
          </div>
        </el-tab-pane>

        <!-- LLM模型配置 -->
        <el-tab-pane label="LLM配置" name="llm">
          <div class="form-section">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="主要LLM模型" prop="llm_model">
                  <el-select 
                    v-model="form.llm_model" 
                    placeholder="选择主要使用的LLM模型"
                    class="full-width"
                    filterable
                  >
                    <el-option
                      v-for="model in availableLLMModels"
                      :key="model.id"
                      :label="model.name || model.model_name"
                      :value="model.id"
                      :disabled="!model.is_available"
                    >
                      <div class="model-option">
                        <span>{{ model.name || model.model_name }}</span>
                        <el-tag 
                          v-if="!model.is_available" 
                          type="danger" 
                          size="small"
                        >
                          不可用
                        </el-tag>
                      </div>
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="工具调用LLM">
                  <el-select 
                    v-model="form.function_calling_llm" 
                    placeholder="选择专门用于工具调用的模型（可选）"
                    class="full-width"
                    filterable
                    clearable
                  >
                    <el-option
                      v-for="model in availableLLMModels"
                      :key="model.id"
                      :label="model.name || model.model_name"
                      :value="model.id"
                      :disabled="!model.is_available"
                    >
                      <div class="model-option">
                        <span>{{ model.name || model.model_name }}</span>
                        <el-tag 
                          v-if="!model.is_available" 
                          type="danger" 
                          size="small"
                        >
                          不可用
                        </el-tag>
                      </div>
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <!-- LLM模型参数配置 -->
            <div v-if="selectedLLMModel" class="llm-params-section">
              <el-divider content-position="left">
                <span class="section-title">模型参数配置</span>
              </el-divider>
              
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="温度参数">
                    <el-slider
                      v-model="llmParams.temperature"
                      :min="0"
                      :max="2"
                      :step="0.1"
                      :format-tooltip="formatTemperature"
                      show-input
                      :show-input-controls="false"
                      input-size="small"
                    />
                    <div class="param-help">控制生成文本的随机性</div>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="最大Token数">
                    <el-input-number
                      v-model="llmParams.max_tokens"
                      :min="1"
                      :max="32000"
                      :step="100"
                      class="full-width"
                      controls-position="right"
                    />
                    <div class="param-help">单次生成的最大token数量</div>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="Top P">
                    <el-slider
                      v-model="llmParams.top_p"
                      :min="0"
                      :max="1"
                      :step="0.05"
                      :format-tooltip="formatTopP"
                      show-input
                      :show-input-controls="false"
                      input-size="small"
                    />
                    <div class="param-help">控制词汇多样性</div>
                  </el-form-item>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-tab-pane>

        <!-- 执行控制 -->
        <el-tab-pane label="执行控制" name="execution">
          <div class="form-section">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="最大迭代次数">
                  <el-input-number
                    v-model="form.max_iter"
                    :min="1"
                    :max="100"
                    class="full-width"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="最大重试次数">
                  <el-input-number
                    v-model="form.max_retry_limit"
                    :min="0"
                    :max="10"
                    class="full-width"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="每分钟最大请求">
                  <el-input-number
                    v-model="form.max_rpm"
                    :min="1"
                    class="full-width"
                    placeholder="不限制"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="最大执行时间(秒)">
                  <el-input-number
                    v-model="form.max_execution_time"
                    :min="1"
                    class="full-width"
                    placeholder="不限制"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="最大推理尝试次数">
                  <el-input-number
                    v-model="form.max_reasoning_attempts"
                    :min="1"
                    :max="10"
                    class="full-width"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="详细日志">
                  <el-switch v-model="form.verbose" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="启用记忆">
                  <el-switch v-model="form.memory" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="允许委托">
                  <el-switch v-model="form.allow_delegation" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="启用推理">
                  <el-switch v-model="form.reasoning" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="多模态支持">
                  <el-switch v-model="form.multimodal" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="注入日期">
                  <el-switch v-model="form.inject_date" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="遵循上下文窗口">
                  <el-switch v-model="form.respect_context_window" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="使用系统提示">
                  <el-switch v-model="form.use_system_prompt" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item v-if="form.inject_date" label="日期格式">
              <el-input 
                v-model="form.date_format" 
                placeholder="%Y-%m-%d %H:%M:%S"
              />
            </el-form-item>
          </div>
        </el-tab-pane>

        <!-- 工具绑定 -->
        <el-tab-pane label="工具配置" name="tools">
          <ToolBindingConfig 
            :agent-id="agent?.id || form.id"
            :available-tools="availableTools"
            @tools-updated="handleToolsUpdated"
          />
        </el-tab-pane>

        <!-- 高级配置 -->
        <el-tab-pane label="高级配置" name="advanced">
          <div class="form-section">
            <el-form-item label="自定义指令">
              <el-input 
                v-model="form.custom_instructions" 
                type="textarea" 
                :rows="4"
                placeholder="输入附加的自定义指令和提示"
              />
            </el-form-item>

            <el-form-item label="步骤回调函数">
              <el-input 
                v-model="form.step_callback" 
                placeholder="每个执行步骤的回调函数名称"
              />
            </el-form-item>

            <el-form-item label="启用监控">
              <el-switch v-model="form.enable_monitoring" />
            </el-form-item>

            <el-form-item label="Agent额外参数">
              <el-input 
                v-model="agentKwargsStr" 
                type="textarea" 
                :rows="6"
                placeholder='输入JSON格式的额外参数，例如：{"custom_param": "value"}'
                @blur="validateAgentKwargs"
              />
              <div class="param-help">传递给CrewAI Agent的其他参数（JSON格式）</div>
            </el-form-item>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button 
          type="primary" 
          :loading="saving"
          @click="handleSave"
        >
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { ElMessage } from 'element-plus'
import ToolBindingConfig from './ToolBindingConfig.vue'
import api from '@/services/api'

export default {
  name: 'AgentConfigDialog',
  components: {
    ToolBindingConfig
  },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    agent: {
      type: Object,
      default: null
    }
  },
  emits: ['update:modelValue', 'saved'],
  data() {
    return {
      visible: false,
      activeTab: 'basic',
      saving: false,
      availableLLMModels: [],
      availableTools: [],
      boundTools: [],
      form: {
        name: '',
        display_name: '',
        description: '',
        role: '',
        goal: '',
        backstory: '',
        llm_model: null,
        function_calling_llm: null,
        verbose: false,
        memory: false,
        max_iter: 20,
        max_rpm: null,
        max_execution_time: null,
        max_retry_limit: 2,
        allow_delegation: false,
        respect_context_window: true,
        use_system_prompt: true,
        multimodal: false,
        inject_date: false,
        date_format: '%Y-%m-%d %H:%M:%S',
        reasoning: false,
        max_reasoning_attempts: 3,
        step_callback: '',
        enable_monitoring: true,
        custom_instructions: '',
        agent_kwargs: {},
        is_active: true,
        is_public: false
      },
      llmParams: {
        temperature: 0.7,
        max_tokens: 4096,
        top_p: 0.9
      },
      agentKwargsStr: '',
      rules: {
        name: [
          { required: true, message: '请输入Agent名称', trigger: 'blur' },
          { min: 1, max: 64, message: '名称长度应在1-64个字符之间', trigger: 'blur' }
        ],
        display_name: [
          { required: true, message: '请输入显示名称', trigger: 'blur' },
          { min: 1, max: 128, message: '显示名称长度应在1-128个字符之间', trigger: 'blur' }
        ],
        role: [
          { required: true, message: '请输入角色定义', trigger: 'blur' },
          { min: 1, max: 128, message: '角色长度应在1-128个字符之间', trigger: 'blur' }
        ],
        goal: [
          { required: true, message: '请输入目标描述', trigger: 'blur' }
        ],
        backstory: [
          { required: true, message: '请输入背景故事', trigger: 'blur' }
        ],
        llm_model: [
          { required: true, message: '请选择LLM模型', trigger: 'change' }
        ]
      }
    }
  },
  computed: {
    isEdit() {
      return !!this.agent
    },
    selectedLLMModel() {
      return this.availableLLMModels.find(model => model.id === this.form.llm_model)
    }
  },
  watch: {
    modelValue: {
      handler(val) {
        this.visible = val
        if (val) {
          this.loadData()
        }
      },
      immediate: true
    },
    visible(val) {
      this.$emit('update:modelValue', val)
    }
  },
  methods: {
    async loadData() {
      await Promise.all([
        this.loadLLMModels(),
        this.loadTools()
      ])
      
      if (this.isEdit) {
        this.loadAgentData()
      } else {
        this.resetForm()
      }
    },

    async loadLLMModels() {
      try {
        const { data } = await api.getAvailableLLMModels()
        this.availableLLMModels = data || []
      } catch (error) {
        console.error('Load LLM models error:', error)
        ElMessage.error('加载LLM模型失败')
      }
    },

    async loadTools() {
      try {
        const { data } = await api.getMCPTools()
        this.availableTools = data.results || []
      } catch (error) {
        console.error('Load tools error:', error)
        ElMessage.error('加载工具列表失败')
      }
    },

    loadAgentData() {
      if (!this.agent) return
      
      // 复制基本信息
      Object.keys(this.form).forEach(key => {
        if (this.agent.hasOwnProperty(key)) {
          this.form[key] = this.agent[key]
        }
      })

      // 处理LLM模型
      if (this.agent.llm_model_info) {
        this.form.llm_model = this.agent.llm_model_info.id
      } else if (this.agent.llm_model) {
        this.form.llm_model = this.agent.llm_model
      }
      if (this.agent.function_calling_llm_info) {
        this.form.function_calling_llm = this.agent.function_calling_llm_info.id
      } else if (this.agent.function_calling_llm) {
        this.form.function_calling_llm = this.agent.function_calling_llm
      }

      // 处理agent_kwargs
      this.agentKwargsStr = JSON.stringify(this.agent.agent_kwargs || {}, null, 2)

      // 加载绑定的工具
      this.loadBoundTools()
    },

    async loadBoundTools() {
      if (!this.agent?.id) return
      
      try {
        const { data } = await api.getAgentTools(this.agent.id)
        this.boundTools = data.results || []
      } catch (error) {
        console.error('Load bound tools error:', error)
      }
    },

    resetForm() {
      this.form = {
        name: '',
        display_name: '',
        description: '',
        role: '',
        goal: '',
        backstory: '',
        llm_model: null,
        function_calling_llm: null,
        verbose: false,
        memory: false,
        max_iter: 20,
        max_rpm: null,
        max_execution_time: null,
        max_retry_limit: 2,
        allow_delegation: false,
        respect_context_window: true,
        use_system_prompt: true,
        multimodal: false,
        inject_date: false,
        date_format: '%Y-%m-%d %H:%M:%S',
        reasoning: false,
        max_reasoning_attempts: 3,
        step_callback: '',
        enable_monitoring: true,
        custom_instructions: '',
        agent_kwargs: {},
        is_active: true,
        is_public: false
      }
      this.agentKwargsStr = ''
      this.boundTools = []
      this.activeTab = 'basic'
    },

    validateAgentKwargs() {
      if (!this.agentKwargsStr.trim()) {
        this.form.agent_kwargs = {}
        return
      }

      try {
        this.form.agent_kwargs = JSON.parse(this.agentKwargsStr)
      } catch (error) {
        ElMessage.warning('Agent额外参数格式不正确，请检查JSON格式')
        this.form.agent_kwargs = {}
      }
    },

    formatTemperature(value) {
      return `${value} (${value < 0.3 ? '保守' : value < 0.7 ? '平衡' : '创新'})`
    },

    formatTopP(value) {
      return `${value} (${value < 0.3 ? '聚焦' : value < 0.7 ? '平衡' : '多样'})`
    },

    handleToolsUpdated() {
      // 重新加载绑定的工具
      this.loadBoundTools()
    },

    async handleSave() {
      try {
        await this.$refs.formRef.validate()
        
        this.validateAgentKwargs()
        
        this.saving = true
        
        if (this.isEdit) {
          await api.updateCrewAIAgent(this.agent.id, this.form)
          ElMessage.success('Agent更新成功')
        } else {
          await api.createCrewAIAgent(this.form)
          ElMessage.success('Agent创建成功')
        }

        this.$emit('saved')
        this.visible = false
      } catch (error) {
        if (error.response?.status === 400 && error.response?.data) {
          const errorData = error.response.data
          
          // 检查是否有非字段错误（业务逻辑错误）
          if (errorData.non_field_errors) {
            const messages = Array.isArray(errorData.non_field_errors) 
              ? errorData.non_field_errors.join('; ')
              : errorData.non_field_errors
            ElMessage.error(messages)
            return
          }
          
          // 检查是否是表单字段验证错误
          if (typeof errorData === 'object' && !errorData.detail && !errorData.message) {
            // 字段验证错误：设置表单字段错误提示
            const formErrors = {}
            for (const [field, messages] of Object.entries(errorData)) {
              if (field === 'non_field_errors') continue // 已处理
              
              if (Array.isArray(messages)) {
                formErrors[field] = messages.join('; ')
              } else {
                formErrors[field] = messages
              }
            }
            
            // 如果有字段错误，设置表单字段错误
            if (Object.keys(formErrors).length > 0) {
              this.$nextTick(() => {
                for (const [field, message] of Object.entries(formErrors)) {
                  this.$refs.formRef?.setFieldError?.(field, message)
                }
              })
              
              ElMessage.warning('请检查并修正表单中的错误')
            }
          } else {
            // 业务逻辑错误：显示toast
            const message = errorData.detail || errorData.message || '操作失败'
            ElMessage.error(message)
          }
        } else if (error.response?.data?.errors) {
          // 旧格式的错误处理（兼容）
          const errors = error.response.data.errors
          const errorMsg = Object.values(errors).flat().join('; ')
          ElMessage.error(errorMsg)
        } else {
          ElMessage.error(this.isEdit ? '更新Agent失败' : '创建Agent失败')
        }
        console.error('Save agent error:', error)
      } finally {
        this.saving = false
      }
    },

    handleCancel() {
      this.visible = false
    },

    handleClosed() {
      this.$refs.formRef?.clearValidate()
    }
  }
}
</script>

<style scoped>
.agent-form {
  max-height: 600px;
  overflow-y: auto;
}

.config-tabs {
  margin-top: 20px;
}

.form-section {
  padding: 20px 0;
}

.section-title {
  font-weight: 600;
  color: #303133;
}

.full-width {
  width: 100%;
}

.model-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.llm-params-section {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.param-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.3;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 自定义滑块样式 */
:deep(.el-slider) {
  margin-right: 12px;
}

:deep(.el-slider__input) {
  width: 80px;
}

/* 自定义标签页样式 */
:deep(.el-tabs__item) {
  font-weight: 500;
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .el-dialog {
    width: 95vw !important;
    margin: 5vh auto !important;
  }
  
  .agent-form {
    max-height: 70vh;
  }
  
  .llm-params-section {
    padding: 12px;
  }
}
</style>
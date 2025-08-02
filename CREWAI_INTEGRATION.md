# CrewAI 平台集成 - 技术迭代文档

## 📋 本次迭代概述

本次迭代旨在为 CrewAI Platform 添加完整的 CrewAI 框架集成功能，包括：
- **LLM 模型配置管理** - 支持多种AI提供商和API验证
- **MCP 工具配置管理** - Model Context Protocol 工具集成
- **CrewAI Agent 配置管理** - 智能代理的完整配置系统
- **Agent-Tool 关联管理** - 代理与工具的动态绑定

## 🎯 核心功能目标

### 1. LLM 模型配置系统
- 支持 OpenAI、Anthropic、Azure、自定义 API 等多种提供商
- 实时 API 连接验证和模型可用性检测
- 安全的 API 密钥加密存储
- 模型参数（温度、token限制）灵活配置
- 动态获取可用模型列表

### 2. MCP 工具配置系统
- 支持 stdio、SSE、HTTP 多种传输协议
- 工具健康检查和状态监控
- JSON Schema 定义工具输入输出
- 超时控制和错误恢复机制
- 动态工具发现和注册

### 3. CrewAI Agent 配置系统
- 完整的 Agent 参数配置支持
- 角色定义、目标设定、背景故事编写
- LLM 模型选择（从配置的模型中选择）
- 工具绑定（多选，支持优先级排序）
- 执行参数调优（迭代次数、超时时间等）

### 4. Agent-Tool 关联系统
- 多对多关系管理
- 工具使用顺序控制
- 个性化工具配置覆盖
- 动态绑定和解绑操作

## 🗃️ 数据库设计

### 表结构概览

```
┌─────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│   llm_model     │────▶│   crewai_agent      │◀────│   mcp_tool      │
│                 │     │                     │     │                 │
│ • 模型配置       │     │ • Agent配置         │     │ • 工具配置       │
│ • API验证        │     │ • 角色目标定义       │     │ • 健康检查       │
│ • 可用性检测      │     │ • LLM模型绑定       │     │ • Schema定义     │
└─────────────────┘     │ • 执行参数控制       │     └─────────────────┘
                        └─────────────────────┘              ▲
                                 │                           │
                                 ▼                           │
                        ┌─────────────────────┐              │
                        │ agent_tool_relation │──────────────┘
                        │                     │
                        │ • 多对多关联         │
                        │ • 使用顺序           │
                        │ • 配置覆盖           │
                        └─────────────────────┘
```

### 1. LLM 模型配置表 (llm_model)

**核心字段**:
- `provider`: AI提供商类型
- `api_base_url`: API基础地址
- `api_key`: 加密存储的API密钥
- `model_info`: 从API动态获取的模型信息
- `is_available`: 实时可用性状态

**关键特性**:
- API连接验证机制
- 模型信息自动同步
- 安全的密钥管理
- 多提供商支持

### 2. MCP 工具配置表 (mcp_tool)

**核心字段**:
- `server_type`: 传输类型 (stdio/sse/http)
- `connection_config`: JSON格式连接配置
- `tool_schema`: 工具输入输出定义
- `health_check_url`: 健康检查端点

**关键特性**:
- 多协议支持
- 动态健康监控
- Schema自动验证
- 错误恢复机制

### 3. CrewAI Agent 配置表 (crewai_agent)

**核心字段**:
- `role`: Agent角色定义
- `goal`: 目标描述
- `backstory`: 背景故事
- `llm_model_id`: 关联LLM模型
- `function_calling_llm_id`: 工具调用专用模型

**关键特性**:
- 完整CrewAI参数支持
- 灵活的LLM模型选择
- 执行控制参数
- 多模态支持

### 4. Agent-Tool 关联表 (agent_tool_relation)

**核心字段**:
- `agent_id`: Agent ID
- `tool_id`: 工具 ID
- `order`: 使用顺序
- `config_override`: 配置覆盖

**关键特性**:
- 多对多关联管理
- 优先级排序
- 个性化配置
- 动态绑定

## 🔧 技术实现架构

### 后端架构 (Django)

```
crewaiplatform/
├── models.py           # 数据模型定义
│   ├── LLMModel       # LLM模型配置
│   ├── MCPTool        # MCP工具配置
│   ├── CrewAIAgent    # Agent配置
│   └── AgentToolRelation # 关联关系
├── services.py         # 业务逻辑层
│   ├── LLMService     # LLM服务管理
│   ├── MCPService     # MCP工具服务
│   ├── AgentService   # Agent服务
│   └── ValidationService # 验证服务
├── views.py           # API视图层
├── serializers.py     # 数据序列化
└── admin.py          # 管理后台
```

### 前端架构 (Vue 3)

```
frontend/src/
├── views/
│   ├── LLMModelManagement.vue    # LLM模型管理
│   ├── MCPToolManagement.vue     # MCP工具管理
│   ├── AgentManagement.vue       # Agent管理（卡片式列表）
│   └── AgentToolBinding.vue      # Agent-Tool绑定
├── components/
│   ├── LLMModelForm.vue          # LLM配置表单
│   ├── MCPToolForm.vue           # MCP工具表单
│   ├── AgentForm.vue             # Agent配置表单
│   ├── AgentCard.vue             # Agent卡片组件
│   ├── AgentConfigDialog.vue     # Agent配置弹窗
│   ├── LLMParamsConfig.vue       # LLM参数配置组件
│   ├── ToolBindingConfig.vue     # 工具绑定配置组件
│   └── ToolSelector.vue          # 工具选择器
└── services/
    ├── llmService.js             # LLM API服务
    ├── mcpService.js             # MCP API服务
    └── agentService.js           # Agent API服务
```

### Agent 卡片式界面设计

#### Agent 卡片布局
```vue
<!-- Agent卡片样式设计 -->
<el-card class="agent-card" shadow="hover">
  <template #header>
    <div class="card-header">
      <span class="agent-name">{{ agent.name }}</span>
      <el-tag :type="agent.is_active ? 'success' : 'danger'">
        {{ agent.is_active ? '激活' : '停用' }}
      </el-tag>
    </div>
  </template>
  
  <div class="agent-info">
    <div class="role-section">
      <el-text class="role-title">角色: {{ agent.role }}</el-text>
      <el-text class="goal-desc" truncated>目标: {{ agent.goal }}</el-text>
    </div>
    
    <div class="model-section">
      <el-text>模型: {{ agent.llm_model?.name }}</el-text>
      <el-text>工具: {{ agent.tools?.length || 0 }} 个</el-text>
    </div>
  </div>
  
  <template #footer>
    <div class="card-actions">
      <el-button-group>
        <el-button size="small" @click="editAgent">配置</el-button>
        <el-button size="small" @click="viewDetails">详情</el-button>
        <el-button size="small" @click="copyAgent">复制</el-button>
        <el-button size="small" type="danger" @click="deleteAgent">删除</el-button>
      </el-button-group>
    </div>
  </template>
</el-card>
```

#### Agent 配置弹窗功能
```vue
<!-- LLM 模型参数配置 -->
<el-form-item label="LLM 模型">
  <el-select v-model="form.llm_model_id" placeholder="选择LLM模型">
    <el-option 
      v-for="model in llmModels" 
      :key="model.id" 
      :label="model.name" 
      :value="model.id"
    />
  </el-select>
</el-form-item>

<el-form-item label="模型参数">
  <el-row :gutter="16">
    <el-col :span="8">
      <el-input v-model="form.temperature" placeholder="温度 (0-1)" />
    </el-col>
    <el-col :span="8">
      <el-input v-model="form.max_tokens" placeholder="最大Token数" />
    </el-col>
    <el-col :span="8">
      <el-input v-model="form.top_p" placeholder="Top P (0-1)" />
    </el-col>
  </el-row>
</el-form-item>

<!-- 工具绑定配置 -->
<el-form-item label="绑定工具">
  <el-transfer
    v-model="selectedTools"
    :data="availableTools"
    :titles="['可用工具', '已绑定工具']"
    :render-content="renderToolItem"
    @change="handleToolChange"
  />
</el-form-item>

<!-- 工具优先级排序 -->
<el-form-item label="工具优先级" v-if="selectedTools.length">
  <draggable v-model="toolPriorities" tag="div" class="tool-list">
    <div v-for="tool in toolPriorities" :key="tool.id" class="tool-item">
      <el-icon><Menu /></el-icon>
      <span>{{ tool.name }}</span>
      <el-button size="small" @click="configTool(tool)">配置</el-button>
    </div>
  </draggable>
</el-form-item>
```

## 🔗 API 接口设计

### LLM 模型管理 API

```
GET    /api/llm-models/           # 获取模型列表
POST   /api/llm-models/           # 创建模型配置
GET    /api/llm-models/{id}/      # 获取模型详情
PUT    /api/llm-models/{id}/      # 更新模型配置
DELETE /api/llm-models/{id}/      # 删除模型配置
POST   /api/llm-models/{id}/validate/  # 验证模型连接
GET    /api/llm-models/{id}/models/    # 获取可用模型列表
```

### MCP 工具管理 API

```
GET    /api/mcp-tools/            # 获取工具列表
POST   /api/mcp-tools/            # 创建工具配置
GET    /api/mcp-tools/{id}/       # 获取工具详情
PUT    /api/mcp-tools/{id}/       # 更新工具配置
DELETE /api/mcp-tools/{id}/       # 删除工具配置
POST   /api/mcp-tools/{id}/health-check/  # 健康检查
```

### CrewAI Agent 管理 API

```
GET    /api/crewai-agents/        # 获取Agent列表
POST   /api/crewai-agents/        # 创建Agent
GET    /api/crewai-agents/{id}/   # 获取Agent详情
PUT    /api/crewai-agents/{id}/   # 更新Agent
DELETE /api/crewai-agents/{id}/   # 删除Agent
GET    /api/crewai-agents/{id}/tools/  # 获取绑定工具
POST   /api/crewai-agents/{id}/tools/  # 绑定工具
DELETE /api/crewai-agents/{id}/tools/{tool_id}/  # 解绑工具
```

### Agent-Tool 关联 API

```
GET    /api/agent-tool-relations/ # 获取关联列表
POST   /api/agent-tool-relations/ # 创建关联
PUT    /api/agent-tool-relations/{id}/  # 更新关联
DELETE /api/agent-tool-relations/{id}/  # 删除关联
```

## 🛡️ 安全设计

### API 密钥管理
- 使用 Django 的加密模块加密存储
- 传输过程中使用 HTTPS
- 前端不直接显示完整密钥
- 支持密钥轮换和撤销

### 访问控制
- 基于现有 RBAC 系统
- 细粒度权限控制
- API 访问日志记录
- 敏感操作审计

### 数据验证
- 严格的输入验证
- JSON Schema 验证
- SQL 注入防护
- XSS 攻击防护

## 🧪 测试策略

### 单元测试
- 模型层测试
- 服务层测试
- API 接口测试
- 前端组件测试

### 集成测试
- API 连接测试
- 工具健康检查测试
- Agent 执行测试
- 数据一致性测试

### 性能测试
- API 响应时间测试
- 并发访问测试
- 大数据量测试
- 内存使用测试

## 🚀 部署和运维

### 环境变量配置
```bash
# CrewAI 配置
CREWAI_DEFAULT_LLM_PROVIDER=openai
CREWAI_DEFAULT_LLM_MODEL=gpt-4
CREWAI_MAX_AGENTS_PER_USER=10
CREWAI_MAX_TOOLS_PER_AGENT=20

# MCP 配置
MCP_HEALTH_CHECK_INTERVAL=300
MCP_CONNECTION_TIMEOUT=30
MCP_RETRY_ATTEMPTS=3

# 安全配置
ENCRYPTION_KEY=your_encryption_key
API_RATE_LIMIT=1000
```

### 监控和日志
- API 调用监控
- 模型使用统计
- 工具健康状态
- 错误日志收集

## 📚 使用场景示例

### 场景1：配置 OpenAI GPT-4 模型
1. 添加 LLM 模型配置
2. 输入 API 密钥和基础 URL
3. 验证连接并获取可用模型
4. 保存配置供 Agent 使用

### 场景2：配置文件操作 MCP 工具
1. 添加 MCP 工具配置
2. 设置 stdio 连接参数
3. 定义工具 Schema
4. 进行健康检查验证

### 场景3：创建数据分析 Agent
1. 定义 Agent 角色和目标
2. 选择 GPT-4 作为主模型
3. 绑定文件操作和数据分析工具
4. 配置执行参数
5. 激活 Agent

## 🔄 迭代计划

### Phase 1: 数据模型和 API (本次)
- 创建数据库表结构
- 实现基础 CRUD API
- 添加数据验证逻辑

### Phase 2: 前端界面
- 实现管理界面
- 添加表单验证
- 集成 API 调用

### Phase 3: 高级功能
- API 验证和模型获取
- 工具健康检查
- Agent 执行引擎

### Phase 4: 优化和扩展
- 性能优化
- 监控和日志
- 扩展功能

---

**文档创建时间**: 2025-08-02  
**技术栈**: Django 4.2+ | Vue 3 | Element Plus | PostgreSQL  
**负责人**: Claude Code Assistant  
**版本**: v1.0  
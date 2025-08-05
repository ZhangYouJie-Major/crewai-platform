# CrewAI Platform 项目结构文档

## 项目概述

CrewAI Platform 是一个基于 Django + Vue.js 的智能代理管理平台，集成了 CrewAI 框架和 MCP (Model Context Protocol) 工具管理。

### 技术栈
- **后端**: Django 4.x + Django REST Framework + PostgreSQL
- **前端**: Vue.js 3.x + Element Plus + Vite
- **AI框架**: CrewAI + LangChain
- **工具协议**: MCP (Model Context Protocol)

## 数据库表结构

### 1. 用户权限管理模块

#### 1.1 用户表 (auth_user)
```sql
-- 继承Django AbstractUser，扩展用户信息
CREATE TABLE auth_user (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL DEFAULT false,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    -- 扩展字段
    phone VARCHAR(11) DEFAULT '',
    avatar VARCHAR(100) DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 1.2 角色表 (sys_role)
```sql
CREATE TABLE sys_role (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    description VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 1.3 权限表 (sys_permission)
```sql
CREATE TABLE sys_permission (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    codename VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 1.4 用户角色关联表 (sys_user_role)
```sql
CREATE TABLE sys_user_role (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES sys_role(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);
```

#### 1.5 角色权限关联表 (sys_role_permission)
```sql
CREATE TABLE sys_role_permission (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES sys_role(id) ON DELETE CASCADE,
    permission_id BIGINT NOT NULL REFERENCES sys_permission(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(role_id, permission_id)
);
```

### 2. AI模型管理模块

#### 2.1 LLM模型配置表 (llm_model)
```sql
CREATE TABLE llm_model (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    provider VARCHAR(32) NOT NULL,  -- openai, anthropic, google等
    model_name VARCHAR(128) NOT NULL,  -- gpt-4, claude-3-sonnet等
    description TEXT DEFAULT '',
    langchain_class VARCHAR(128) DEFAULT 'ChatOpenAI',
    api_base_url VARCHAR(255) DEFAULT '',
    api_key VARCHAR(255) DEFAULT '',  -- 加密存储
    api_version VARCHAR(20) DEFAULT '',
    temperature DECIMAL(3,2) DEFAULT 0.70,
    max_tokens INTEGER DEFAULT 4096,
    timeout INTEGER DEFAULT 30,
    max_retries INTEGER DEFAULT 3,
    extra_kwargs JSONB DEFAULT '{}',
    model_kwargs JSONB DEFAULT '{}',
    model_info JSONB DEFAULT '{}',
    last_validated TIMESTAMP WITH TIME ZONE,
    is_available BOOLEAN DEFAULT false,
    validation_error TEXT DEFAULT '',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. MCP工具管理模块

#### 3.1 MCP工具配置表 (mcp_tool)
```sql
CREATE TABLE mcp_tool (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    display_name VARCHAR(128) DEFAULT '',
    description TEXT DEFAULT '',
    version VARCHAR(32) DEFAULT '',
    server_type VARCHAR(32) NOT NULL,  -- stdio, sse, http
    connection_config JSONB NOT NULL DEFAULT '{}',
    tool_schema JSONB DEFAULT '{}',
    connection_timeout INTEGER DEFAULT 30,
    request_timeout INTEGER DEFAULT 60,
    max_retries INTEGER DEFAULT 3,
    retry_delay DECIMAL(3,1) DEFAULT 1.0,
    health_check_enabled BOOLEAN DEFAULT true,
    health_check_interval INTEGER DEFAULT 300,
    health_check_method VARCHAR(64) DEFAULT 'ping',
    status VARCHAR(32) DEFAULT 'unknown',  -- unknown, healthy, unhealthy, error
    last_health_check TIMESTAMP WITH TIME ZONE,
    last_error TEXT DEFAULT '',
    response_time_ms INTEGER,
    total_calls INTEGER DEFAULT 0,
    success_calls INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    is_public BOOLEAN DEFAULT false,
    allowed_users JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. CrewAI Agent管理模块

#### 4.1 CrewAI Agent配置表 (crewai_agent)
```sql
CREATE TABLE crewai_agent (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    display_name VARCHAR(128) DEFAULT '',
    description TEXT DEFAULT '',
    role VARCHAR(128) NOT NULL,  -- 角色定义
    goal TEXT NOT NULL,  -- 目标描述
    backstory TEXT DEFAULT '',  -- 背景故事
    llm_model_id BIGINT REFERENCES llm_model(id),
    function_calling_llm_id BIGINT REFERENCES llm_model(id),
    verbose BOOLEAN DEFAULT false,
    memory BOOLEAN DEFAULT false,
    max_iter INTEGER DEFAULT 20,
    max_rpm INTEGER,
    max_execution_time INTEGER,
    max_retry_limit INTEGER DEFAULT 2,
    allow_delegation BOOLEAN DEFAULT false,
    respect_context_window BOOLEAN DEFAULT true,
    use_system_prompt BOOLEAN DEFAULT true,
    multimodal BOOLEAN DEFAULT false,
    inject_date BOOLEAN DEFAULT false,
    date_format VARCHAR(32) DEFAULT '%Y-%m-%d %H:%M:%S',
    reasoning BOOLEAN DEFAULT false,
    max_reasoning_attempts INTEGER DEFAULT 3,
    step_callback VARCHAR(255) DEFAULT '',
    enable_monitoring BOOLEAN DEFAULT true,
    custom_instructions TEXT DEFAULT '',
    agent_kwargs JSONB DEFAULT '{}',
    status VARCHAR(32) DEFAULT 'inactive',  -- inactive, active, running, paused, error
    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    total_execution_time INTEGER DEFAULT 0,
    last_execution TIMESTAMP WITH TIME ZONE,
    last_error TEXT DEFAULT '',
    is_active BOOLEAN DEFAULT true,
    is_public BOOLEAN DEFAULT false,
    owner_id BIGINT REFERENCES auth_user(id),
    allowed_users JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 4.2 Agent-Tool关联表 (agent_tool_relation)
```sql
CREATE TABLE agent_tool_relation (
    id BIGSERIAL PRIMARY KEY,
    agent_id BIGINT NOT NULL REFERENCES crewai_agent(id) ON DELETE CASCADE,
    tool_id BIGINT NOT NULL REFERENCES mcp_tool(id) ON DELETE CASCADE,
    order INTEGER DEFAULT 0,  -- 使用优先级
    is_required BOOLEAN DEFAULT false,  -- 是否必需
    is_fallback BOOLEAN DEFAULT false,  -- 是否为备用工具
    max_calls_per_task INTEGER,
    config_override JSONB DEFAULT '{}',  -- 配置覆盖
    prompt_template TEXT DEFAULT '',  -- 自定义提示模板
    permission_level VARCHAR(32) DEFAULT 'read',  -- read, write, execute, admin
    allowed_operations JSONB DEFAULT '[]',  -- 允许的操作列表
    restricted_paths JSONB DEFAULT '[]',  -- 限制路径
    status VARCHAR(32) DEFAULT 'active',  -- active, inactive, error, deprecated
    total_calls INTEGER DEFAULT 0,
    successful_calls INTEGER DEFAULT 0,
    total_execution_time INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,
    last_error TEXT DEFAULT '',
    config_version VARCHAR(32) DEFAULT '1.0',
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(agent_id, tool_id)
);
```

### 5. 字典管理模块

#### 5.1 字典表 (dictionary)
```sql
CREATE TABLE dictionary (
    id BIGSERIAL PRIMARY KEY,
    parent_id BIGINT REFERENCES dictionary(id) ON DELETE CASCADE,  -- 自关联，支持层级结构
    code VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    value TEXT DEFAULT '',
    description TEXT DEFAULT '',
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(parent_id, code)  -- 同一父级下code唯一
);
```

## 表关联关系

### 1. 用户权限关联关系
```
auth_user (用户)
    ↓ (多对多)
sys_user_role (用户角色关联)
    ↓ (多对一)
sys_role (角色)
    ↓ (多对多)
sys_role_permission (角色权限关联)
    ↓ (多对一)
sys_permission (权限)
```

### 2. AI模型关联关系
```
crewai_agent (Agent)
    ↓ (多对一)
llm_model (LLM模型) ← 主要模型
llm_model (LLM模型) ← 工具调用模型
```

### 3. Agent-Tool关联关系
```
crewai_agent (Agent)
    ↓ (多对多)
agent_tool_relation (Agent-Tool关联)
    ↓ (多对一)
mcp_tool (MCP工具)
```

### 4. 字典层级关系
```
dictionary (字典)
    ↓ (自关联)
dictionary (子字典项)
    ↓ (自关联)
dictionary (孙字典项)
```

### 5. 用户与资源关联关系
```
auth_user (用户)
    ↓ (一对多)
crewai_agent (Agent) ← 所有者
mcp_tool (MCP工具) ← 允许使用的用户(JSONB)
```

## 项目架构

### 后端架构 (Django)

```
backend/
├── crewaiplatform/
│   ├── models/           # 数据模型层
│   │   ├── user.py      # 用户模型
│   │   ├── role.py      # 角色模型
│   │   ├── permission.py # 权限模型
│   │   ├── llm_model.py # LLM模型
│   │   ├── mcp_tool.py  # MCP工具
│   │   ├── crewai_agent.py # Agent模型
│   │   ├── agent_tool_relation.py # 关联模型
│   │   └── dictionary.py # 字典模型
│   ├── services/         # 业务逻辑层
│   │   ├── auth_service.py # 认证服务
│   │   ├── rbac_service.py # 权限服务
│   │   ├── llm_service.py # LLM服务
│   │   ├── mcp_service.py # MCP服务
│   │   └── agent_service.py # Agent服务
│   ├── views/           # 视图控制层
│   │   ├── auth_views.py # 认证视图
│   │   ├── crewai_views.py # CrewAI视图
│   │   └── user_views.py # 用户视图
│   ├── serializers/     # 序列化层
│   │   ├── auth_serializers.py
│   │   ├── crewai_serializers.py
│   │   └── rbac_serializers.py
│   └── tests/          # 测试层
```

### 前端架构 (Vue.js)

```
frontend/src/
├── components/          # 组件层
│   ├── AgentCard.vue   # Agent卡片组件
│   ├── MCPToolCard.vue # MCP工具卡片
│   └── ...
├── views/              # 页面层
│   ├── Dashboard.vue   # 仪表盘
│   ├── AgentManagement.vue # Agent管理
│   ├── MCPToolManagement.vue # 工具管理
│   └── ...
├── services/           # 服务层
│   └── api.js         # API接口
├── store/             # 状态管理
│   └── index.js       # Vuex配置
└── router/            # 路由层
    └── index.js       # 路由配置
```

## 核心功能模块

### 1. 用户权限管理 (RBAC)
- 用户注册、登录、认证
- 角色管理（超级管理员、管理员、用户）
- 权限管理（细粒度权限控制）
- 用户角色分配

### 2. LLM模型管理
- 支持多种LLM提供商（OpenAI、Anthropic、Google等）
- 模型配置管理（API密钥、参数设置）
- 模型连接测试和状态监控
- 模型使用统计

### 3. MCP工具管理
- MCP工具配置和连接管理
- 支持多种传输协议（stdio、SSE、HTTP）
- 工具健康检查和状态监控
- 工具使用统计和错误追踪

### 4. CrewAI Agent管理
- Agent创建和配置管理
- 角色定义和目标设置
- LLM模型绑定
- 工具绑定和权限控制
- Agent执行状态监控

### 5. 字典管理
- 支持层级结构的字典数据
- 用于系统配置和选项管理
- 支持LLM供应商、模型类型等分类

## 数据流

### 1. 用户认证流程
```
用户登录 → 验证凭据 → 生成JWT Token → 返回用户信息和权限
```

### 2. Agent执行流程
```
用户提交任务 → 选择Agent → 加载配置 → 绑定工具 → 执行任务 → 返回结果
```

### 3. 工具调用流程
```
Agent需要工具 → 检查权限 → 调用MCP工具 → 处理结果 → 返回给Agent
```

## 安全机制

### 1. 认证安全
- JWT Token认证
- 密码加密存储
- 会话管理

### 2. 权限控制
- 基于角色的访问控制(RBAC)
- 细粒度权限管理
- API接口权限验证

### 3. 数据安全
- API密钥加密存储
- 敏感信息脱敏
- 操作日志记录

## 部署架构

### 开发环境
```
前端 (Vue.js) → 后端 (Django) → 数据库 (PostgreSQL)
    ↓              ↓
  Vite Dev Server  Django Dev Server
```

### 生产环境
```
Nginx → 前端静态文件
  ↓
Nginx → Gunicorn → Django → PostgreSQL
```

## 监控和日志

### 1. 系统监控
- 数据库连接状态
- API响应时间
- 错误率统计

### 2. 业务监控
- Agent执行统计
- 工具调用统计
- 用户活跃度

### 3. 日志记录
- 操作审计日志
- 错误日志
- 性能日志

## 扩展性设计

### 1. 模块化架构
- 清晰的层次分离
- 松耦合的模块设计
- 易于扩展和维护

### 2. 插件化设计
- MCP工具可插拔
- LLM模型可扩展
- Agent模板可复用

### 3. 配置化管理
- 字典驱动的配置管理
- 环境变量配置
- 动态配置更新

## 性能优化

### 1. 数据库优化
- 合理的索引设计
- 查询优化
- 连接池管理

### 2. 缓存策略
- Redis缓存
- 查询结果缓存
- 静态资源缓存

### 3. 异步处理
- 任务队列
- 异步API调用
- 后台任务处理

## 开发规范

### 1. 代码规范
- Python PEP8规范
- JavaScript ESLint规范
- 统一的命名规范

### 2. 文档规范
- API文档自动生成
- 代码注释规范
- 架构文档维护

### 3. 测试规范
- 单元测试覆盖
- 集成测试
- 自动化测试

## 总结

CrewAI Platform 是一个功能完整、架构清晰的智能代理管理平台，具备以下特点：

1. **完整的权限管理体系** - 基于RBAC的用户权限控制
2. **灵活的AI模型管理** - 支持多种LLM提供商和模型
3. **强大的工具集成** - 基于MCP协议的工具管理
4. **智能的Agent管理** - 基于CrewAI框架的智能代理
5. **可扩展的架构设计** - 模块化、插件化的系统架构
6. **完善的监控体系** - 全面的日志和监控机制

该平台为AI应用开发提供了完整的工具链和管理体系，支持从模型配置到Agent部署的全流程管理。 
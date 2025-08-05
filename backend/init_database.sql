-- CrewAI Platform 数据库初始化脚本
-- 基于实际models代码生成的完整DDL和DML
-- 适用于PostgreSQL数据库

-- ==========================================
-- 1. 数据库表结构 (DDL)
-- ==========================================

-- 1.1 用户表 (继承Django AbstractUser)
CREATE TABLE IF NOT EXISTS auth_user (
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

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_auth_user_username ON auth_user(username);
CREATE INDEX IF NOT EXISTS idx_auth_user_email ON auth_user(email);
CREATE INDEX IF NOT EXISTS idx_auth_user_is_active ON auth_user(is_active);

-- 1.2 角色表
CREATE TABLE IF NOT EXISTS sys_role (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    description VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 角色表索引
CREATE INDEX IF NOT EXISTS idx_sys_role_name ON sys_role(name);

-- 1.3 权限表
CREATE TABLE IF NOT EXISTS sys_permission (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    codename VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 权限表索引
CREATE INDEX IF NOT EXISTS idx_sys_permission_name ON sys_permission(name);
CREATE INDEX IF NOT EXISTS idx_sys_permission_codename ON sys_permission(codename);

-- 1.4 用户角色关联表
CREATE TABLE IF NOT EXISTS sys_user_role (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES sys_role(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);

-- 用户角色关联表索引
CREATE INDEX IF NOT EXISTS idx_sys_user_role_user_id ON sys_user_role(user_id);
CREATE INDEX IF NOT EXISTS idx_sys_user_role_role_id ON sys_user_role(role_id);

-- 1.5 角色权限关联表
CREATE TABLE IF NOT EXISTS sys_role_permission (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES sys_role(id) ON DELETE CASCADE,
    permission_id BIGINT NOT NULL REFERENCES sys_permission(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(role_id, permission_id)
);

-- 角色权限关联表索引
CREATE INDEX IF NOT EXISTS idx_sys_role_permission_role_id ON sys_role_permission(role_id);
CREATE INDEX IF NOT EXISTS idx_sys_role_permission_permission_id ON sys_role_permission(permission_id);

-- 1.6 LLM模型配置表
CREATE TABLE IF NOT EXISTS llm_model (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    provider VARCHAR(32) NOT NULL,
    model_name VARCHAR(128) NOT NULL,
    description TEXT DEFAULT '',
    langchain_class VARCHAR(128) DEFAULT 'ChatOpenAI',
    api_base_url VARCHAR(255) DEFAULT '',
    api_key VARCHAR(255) DEFAULT '',
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

-- LLM模型表索引
CREATE INDEX IF NOT EXISTS idx_llm_model_provider ON llm_model(provider);
CREATE INDEX IF NOT EXISTS idx_llm_model_is_active ON llm_model(is_active);
CREATE INDEX IF NOT EXISTS idx_llm_model_is_available ON llm_model(is_available);

-- 1.7 MCP工具配置表
CREATE TABLE IF NOT EXISTS mcp_tool (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    display_name VARCHAR(128) DEFAULT '',
    description TEXT DEFAULT '',
    version VARCHAR(32) DEFAULT '',
    server_type VARCHAR(32) NOT NULL,
    connection_config JSONB NOT NULL DEFAULT '{}',
    tool_schema JSONB DEFAULT '{}',
    connection_timeout INTEGER DEFAULT 30,
    request_timeout INTEGER DEFAULT 60,
    max_retries INTEGER DEFAULT 3,
    retry_delay DECIMAL(3,1) DEFAULT 1.0,
    health_check_enabled BOOLEAN DEFAULT true,
    health_check_interval INTEGER DEFAULT 300,
    health_check_method VARCHAR(64) DEFAULT 'ping',
    status VARCHAR(32) DEFAULT 'unknown',
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

-- MCP工具表索引
CREATE INDEX IF NOT EXISTS idx_mcp_tool_server_type ON mcp_tool(server_type);
CREATE INDEX IF NOT EXISTS idx_mcp_tool_status ON mcp_tool(status);
CREATE INDEX IF NOT EXISTS idx_mcp_tool_is_active ON mcp_tool(is_active);

-- 1.8 CrewAI Agent配置表
CREATE TABLE IF NOT EXISTS crewai_agent (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    display_name VARCHAR(128) DEFAULT '',
    description TEXT DEFAULT '',
    role VARCHAR(128) NOT NULL,
    goal TEXT NOT NULL,
    backstory TEXT DEFAULT '',
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
    status VARCHAR(32) DEFAULT 'inactive',
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

-- CrewAI Agent表索引
CREATE INDEX IF NOT EXISTS idx_crewai_agent_owner_id ON crewai_agent(owner_id);
CREATE INDEX IF NOT EXISTS idx_crewai_agent_status ON crewai_agent(status);
CREATE INDEX IF NOT EXISTS idx_crewai_agent_is_active ON crewai_agent(is_active);

-- 1.9 Agent-Tool关联表
CREATE TABLE IF NOT EXISTS agent_tool_relation (
    id BIGSERIAL PRIMARY KEY,
    agent_id BIGINT NOT NULL REFERENCES crewai_agent(id) ON DELETE CASCADE,
    tool_id BIGINT NOT NULL REFERENCES mcp_tool(id) ON DELETE CASCADE,
    order INTEGER DEFAULT 0,
    is_required BOOLEAN DEFAULT false,
    is_fallback BOOLEAN DEFAULT false,
    max_calls_per_task INTEGER,
    config_override JSONB DEFAULT '{}',
    prompt_template TEXT DEFAULT '',
    permission_level VARCHAR(32) DEFAULT 'read',
    allowed_operations JSONB DEFAULT '[]',
    restricted_paths JSONB DEFAULT '[]',
    status VARCHAR(32) DEFAULT 'active',
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

-- Agent-Tool关联表索引
CREATE INDEX IF NOT EXISTS idx_agent_tool_relation_agent_id ON agent_tool_relation(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_tool_relation_tool_id ON agent_tool_relation(tool_id);
CREATE INDEX IF NOT EXISTS idx_agent_tool_relation_status ON agent_tool_relation(status);

-- 1.10 字典表 (支持自关联层级结构)
CREATE TABLE IF NOT EXISTS dictionary (
    id BIGSERIAL PRIMARY KEY,
    parent_id BIGINT REFERENCES dictionary(id) ON DELETE CASCADE,
    code VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    value TEXT DEFAULT '',
    description TEXT DEFAULT '',
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(parent_id, code)
);

-- 字典表索引
CREATE INDEX IF NOT EXISTS idx_dictionary_parent_id ON dictionary(parent_id);
CREATE INDEX IF NOT EXISTS idx_dictionary_code ON dictionary(code);
CREATE INDEX IF NOT EXISTS idx_dictionary_is_active ON dictionary(is_active);

-- ==========================================
-- 2. 触发器函数
-- ==========================================

-- 更新updated_at字段的触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表创建触发器
CREATE TRIGGER update_auth_user_updated_at 
    BEFORE UPDATE ON auth_user 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sys_role_updated_at 
    BEFORE UPDATE ON sys_role 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sys_permission_updated_at 
    BEFORE UPDATE ON sys_permission 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_llm_model_updated_at 
    BEFORE UPDATE ON llm_model 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mcp_tool_updated_at 
    BEFORE UPDATE ON mcp_tool 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_crewai_agent_updated_at 
    BEFORE UPDATE ON crewai_agent 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_tool_relation_updated_at 
    BEFORE UPDATE ON agent_tool_relation 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dictionary_updated_at 
    BEFORE UPDATE ON dictionary 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- 3. 基础数据插入 (DML)
-- ==========================================

-- 3.1 插入默认角色
INSERT INTO sys_role (name, description) VALUES 
('超级管理员', '系统最高权限管理员'),
('管理员', '系统管理员'),
('用户', '普通用户')
ON CONFLICT (name) DO NOTHING;

-- 3.2 插入默认权限
INSERT INTO sys_permission (name, codename, description) VALUES
('用户管理', 'manage_users', '管理用户账户'),
('角色管理', 'manage_roles', '管理系统角色'),
('权限管理', 'manage_permissions', '管理系统权限'),
('查看仪表盘', 'view_dashboard', '查看系统仪表盘'),
('系统配置', 'system_config', '修改系统配置'),
('LLM模型管理', 'manage_llm_models', '管理LLM模型配置'),
('MCP工具管理', 'manage_mcp_tools', '管理MCP工具配置'),
('Agent管理', 'manage_agents', '管理CrewAI Agent'),
('字典管理', 'manage_dictionaries', '管理系统字典')
ON CONFLICT (codename) DO NOTHING;

-- 3.3 为超级管理员分配所有权限
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT 
    (SELECT id FROM sys_role WHERE name = '超级管理员'),
    id
FROM sys_permission
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 3.4 为管理员分配部分权限
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT 
    (SELECT id FROM sys_role WHERE name = '管理员'),
    id
FROM sys_permission 
WHERE codename IN ('manage_users', 'view_dashboard', 'manage_llm_models', 'manage_mcp_tools', 'manage_agents', 'manage_dictionaries')
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 3.5 为普通用户分配基础权限
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT 
    (SELECT id FROM sys_role WHERE name = '用户'),
    id
FROM sys_permission 
WHERE codename IN ('view_dashboard')
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 3.6 插入基础LLM模型配置
INSERT INTO llm_model (name, provider, model_name, description, temperature, max_tokens, timeout, is_active) VALUES
('OpenAI GPT-4', 'openai', 'gpt-4', 'OpenAI GPT-4 模型，适用于复杂的推理和生成任务', 0.7, 4096, 30, false),
('OpenAI GPT-3.5 Turbo', 'openai', 'gpt-3.5-turbo', 'OpenAI GPT-3.5 Turbo 模型，高性价比的对话模型', 0.7, 4096, 30, false),
('Anthropic Claude-3.5 Sonnet', 'anthropic', 'claude-3-5-sonnet-20241022', 'Anthropic Claude-3.5 Sonnet 模型，擅长分析和推理', 0.7, 4096, 30, false)
ON CONFLICT (name) DO NOTHING;

-- 3.7 插入基础字典数据
INSERT INTO dictionary (code, name, description, sort_order) VALUES
('llm_provider', 'LLM供应商', 'LLM大语言模型提供商分类', 1),
('mcp_server_type', 'MCP服务器类型', 'MCP工具服务器类型分类', 2)
ON CONFLICT (code) DO NOTHING;

-- 3.8 插入LLM供应商字典项
INSERT INTO dictionary (parent_id, code, name, description, sort_order) VALUES
((SELECT id FROM dictionary WHERE code = 'llm_provider'), 'openai', 'OpenAI', 'OpenAI公司提供的大语言模型服务', 1),
((SELECT id FROM dictionary WHERE code = 'llm_provider'), 'anthropic', 'Anthropic', 'Anthropic公司提供的Claude系列模型', 2),
((SELECT id FROM dictionary WHERE code = 'llm_provider'), 'google', 'Google', 'Google公司提供的Gemini系列模型', 3),
((SELECT id FROM dictionary WHERE code = 'llm_provider'), 'baidu', '百度', '百度公司提供的文心一言系列模型', 4),
((SELECT id FROM dictionary WHERE code = 'llm_provider'), 'alibaba', '阿里云', '阿里云提供的通义千问系列模型', 5)
ON CONFLICT (parent_id, code) DO NOTHING;

-- 3.9 插入MCP服务器类型字典项
INSERT INTO dictionary (parent_id, code, name, description, sort_order) VALUES
((SELECT id FROM dictionary WHERE code = 'mcp_server_type'), 'stdio', 'Standard I/O', '基于标准输入输出的MCP服务器', 1),
((SELECT id FROM dictionary WHERE code = 'mcp_server_type'), 'sse', 'Server-Sent Events', '基于HTTP流式传输的MCP服务器', 2),
((SELECT id FROM dictionary WHERE code = 'mcp_server_type'), 'http', 'HTTP', '基于HTTP请求响应的MCP服务器', 3)
ON CONFLICT (parent_id, code) DO NOTHING;

-- ==========================================
-- 4. 创建视图
-- ==========================================

-- 用户权限视图
CREATE OR REPLACE VIEW user_permissions AS
SELECT 
    u.id as user_id,
    u.username,
    r.name as role_name,
    p.name as permission_name,
    p.codename as permission_codename
FROM auth_user u
JOIN sys_user_role ur ON u.id = ur.user_id
JOIN sys_role r ON ur.role_id = r.id
JOIN sys_role_permission rp ON r.id = rp.role_id
JOIN sys_permission p ON rp.permission_id = p.id
WHERE u.is_active = true AND r.id IS NOT NULL;

-- 系统统计视图
CREATE OR REPLACE VIEW system_stats AS
SELECT 
    (SELECT COUNT(*) FROM auth_user WHERE is_active = true) as total_users,
    (SELECT COUNT(*) FROM sys_role) as total_roles,
    (SELECT COUNT(*) FROM sys_permission) as total_permissions,
    (SELECT COUNT(*) FROM llm_model WHERE is_active = true) as total_llm_models,
    (SELECT COUNT(*) FROM mcp_tool WHERE is_active = true) as total_mcp_tools,
    (SELECT COUNT(*) FROM crewai_agent WHERE is_active = true) as total_agents,
    (SELECT COUNT(*) FROM dictionary WHERE is_active = true) as total_dictionaries;

-- ==========================================
-- 初始化完成
-- ==========================================

COMMIT;

-- 显示初始化结果
SELECT '数据库初始化完成！' as message;
SELECT '表结构创建完成' as table_status;
SELECT '基础数据插入完成' as data_status;
SELECT '触发器创建完成' as trigger_status;
SELECT '视图创建完成' as view_status; 
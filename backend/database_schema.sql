-- CrewAI Platform 数据库表结构 DDL
-- 适用于PostgreSQL数据库

-- 1. 用户表 (继承Django AbstractUser)
CREATE TABLE auth_user (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(254),
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT true,
    is_staff BOOLEAN DEFAULT false,
    is_superuser BOOLEAN DEFAULT false,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    -- 扩展字段
    phone VARCHAR(11),
    avatar VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户表索引
CREATE INDEX idx_auth_user_username ON auth_user(username);
CREATE INDEX idx_auth_user_email ON auth_user(email);
CREATE INDEX idx_auth_user_is_active ON auth_user(is_active);

-- 2. 角色表
CREATE TABLE sys_role (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 角色表索引
CREATE INDEX idx_sys_role_name ON sys_role(name);

-- 3. 权限表
CREATE TABLE sys_permission (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    codename VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 权限表索引
CREATE INDEX idx_sys_permission_name ON sys_permission(name);
CREATE INDEX idx_sys_permission_codename ON sys_permission(codename);

-- 4. 用户角色关联表
CREATE TABLE sys_user_role (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES sys_role(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);

-- 用户角色关联表索引
CREATE INDEX idx_sys_user_role_user_id ON sys_user_role(user_id);
CREATE INDEX idx_sys_user_role_role_id ON sys_user_role(role_id);

-- 5. 角色权限关联表
CREATE TABLE sys_role_permission (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES sys_role(id) ON DELETE CASCADE,
    permission_id BIGINT NOT NULL REFERENCES sys_permission(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(role_id, permission_id)
);

-- 角色权限关联表索引
CREATE INDEX idx_sys_role_permission_role_id ON sys_role_permission(role_id);
CREATE INDEX idx_sys_role_permission_permission_id ON sys_role_permission(permission_id);

-- 初始化数据

-- 插入默认角色
INSERT INTO sys_role (name, description) VALUES 
('超级管理员', '系统最高权限管理员'),
('管理员', '系统管理员'),
('用户', '普通用户');

-- 插入默认权限
INSERT INTO sys_permission (name, codename, description) VALUES
('用户管理', 'manage_users', '管理用户账户'),
('角色管理', 'manage_roles', '管理系统角色'),
('权限管理', 'manage_permissions', '管理系统权限'),
('查看仪表盘', 'view_dashboard', '查看系统仪表盘'),
('系统配置', 'system_config', '修改系统配置');

-- 为超级管理员分配所有权限
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT 
    (SELECT id FROM sys_role WHERE name = '超级管理员'),
    id
FROM sys_permission;

-- 为管理员分配部分权限
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT 
    (SELECT id FROM sys_role WHERE name = '管理员'),
    id
FROM sys_permission 
WHERE codename IN ('manage_users', 'view_dashboard');

-- 为普通用户分配基础权限
INSERT INTO sys_role_permission (role_id, permission_id)
SELECT 
    (SELECT id FROM sys_role WHERE name = '用户'),
    id
FROM sys_permission 
WHERE codename = 'view_dashboard';

-- 创建自动更新updated_at字段的触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表创建触发器
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

-- 查询用户权限的视图（可选）
CREATE VIEW user_permissions AS
SELECT 
    u.id as user_id,
    u.username,
    r.name as role_name,
    p.name as permission_name,
    p.codename as permission_code
FROM auth_user u
JOIN sys_user_role ur ON u.id = ur.user_id
JOIN sys_role r ON ur.role_id = r.id
JOIN sys_role_permission rp ON r.id = rp.role_id
JOIN sys_permission p ON rp.permission_id = p.id
WHERE u.is_active = true;

-- 统计信息视图
CREATE VIEW system_stats AS
SELECT 
    (SELECT COUNT(*) FROM auth_user WHERE is_active = true) as active_users,
    (SELECT COUNT(*) FROM auth_user WHERE is_staff = true) as staff_users,
    (SELECT COUNT(*) FROM sys_role) as total_roles,
    (SELECT COUNT(*) FROM sys_permission) as total_permissions,
    (SELECT COUNT(*) FROM sys_user_role) as user_role_assignments,
    (SELECT COUNT(*) FROM sys_role_permission) as role_permission_assignments;
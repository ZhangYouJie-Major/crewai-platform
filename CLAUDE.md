# CrewAI Platform - Django标准分层架构

## 项目概述

CrewAI Platform 是一个采用 **Django标准分层架构** 的现代化RBAC（基于角色的访问控制）管理平台。项目采用前后端分离设计，后端使用 Django 单应用架构提供API服务，前端使用 Vue 3 + Element Plus 构建响应式用户界面。

### 核心特性
- 🏗️ **Django单应用架构**: 采用Django项目标准的单应用分层结构
- 🔐 **完整RBAC系统**: 用户、角色、权限的灵活管理
- 🚀 **现代化技术栈**: Django 4.2+ & Vue 3 & Element Plus
- 📱 **响应式设计**: 支持桌面端和移动端
- 🌐 **RESTful API**: 标准化的API设计
- 🔄 **实时数据更新**: 动态加载，非静态数据展示
- 🛡️ **安全性**: JWT认证，环境变量配置，跨域保护

## 项目架构

### 整体项目结构

```
crewai-platform/
├── backend/                    # Django 后端
├── frontend/                   # Vue.js 前端  
├── scripts/                    # 初始化和管理脚本
│   ├── init_backend.sh        # 后端完整初始化
│   ├── init_frontend.sh       # 前端完整初始化
│   ├── init_data.sh           # 数据库数据初始化
│   ├── reset_database.sh      # 数据库重置
│   ├── reset_and_init.sh      # 一键重置并初始化
│   └── README.md              # 脚本使用说明
├── start_all.sh               # 一键启动前后端
├── stop_all.sh                # 停止所有服务
├── dev.sh                     # 开发工具集合
└── CLAUDE.md                  # 项目文档
```

### 后端架构 (Django标准分层)

```
backend/
├── crewaiplatform/           # Django项目主目录
│   ├── __init__.py          # 包初始化文件
│   ├── settings.py          # 项目配置（环境变量驱动）
│   ├── urls.py              # 路由配置
│   ├── wsgi.py              # WSGI部署配置
│   ├── asgi.py              # ASGI配置
│   ├── apps.py              # 应用配置
│   ├── models.py            # 数据模型层
│   ├── views.py             # 视图控制层
│   ├── serializers.py       # 数据序列化层
│   ├── services.py          # 业务逻辑层
│   └── admin.py             # Django管理后台
├── migrations/              # 数据库迁移文件
├── logs/                    # 日志文件目录
├── pyproject.toml           # Python项目配置和依赖
├── manage.py                # Django管理脚本
├── start.sh                 # 日常启动脚本
└── database_schema.sql      # 数据库DDL脚本
```

### 前端架构 (简化结构)

```
frontend/
├── src/
│   ├── views/               # 页面组件
│   │   ├── Dashboard.vue    # 仪表盘（动态数据）
│   │   ├── Login.vue        # 登录页面
│   │   ├── Register.vue     # 注册页面
│   │   └── ...
│   ├── services/            # API服务层
│   │   └── api.js           # 统一API调用封装
│   ├── store/               # 状态管理
│   │   └── index.js         # 简化状态管理
│   ├── router/              # 路由配置
│   │   └── index.js
│   ├── components/          # 公共组件
│   ├── http.js              # HTTP客户端配置
│   └── main.js              # 应用入口
├── .env                     # 环境变量配置
├── .env.development         # 开发环境配置
├── .env.production          # 生产环境配置
└── package.json             # 前端依赖配置
```

## 数据库设计

### 数据库表结构

项目采用标准的RBAC（基于角色的访问控制）五表设计，包含用户、角色、权限及其关联关系表。

#### 1. 用户表 (auth_user)

| 字段名 | 类型 | 长度 | 约束 | 说明 |
|--------|------|------|------|------|
| id | BigAutoField | - | 主键,自增 | 用户唯一标识 |
| username | CharField | 150 | 唯一,非空 | 用户名,用于登录 |
| password | CharField | 128 | 非空 | 加密后的密码 |
| email | EmailField | 254 | - | 邮箱地址 |
| first_name | CharField | 150 | - | 名字 |
| last_name | CharField | 150 | - | 姓氏 |
| is_active | BooleanField | - | 默认True | 用户是否激活 |
| is_staff | BooleanField | - | 默认False | 是否为员工 |
| is_superuser | BooleanField | - | 默认False | 是否为超级用户 |
| date_joined | DateTimeField | - | 自动添加 | 注册时间 |
| last_login | DateTimeField | - | 可为空 | 最后登录时间 |
| phone | CharField | 11 | 可为空 | 手机号码 |
| avatar | ImageField | - | 可为空 | 用户头像 |
| created_at | DateTimeField | - | 自动添加 | 创建时间 |
| updated_at | DateTimeField | - | 自动更新 | 更新时间 |

**用途**: 存储系统用户基本信息，继承Django AbstractUser模型，包含认证和授权所需的基础字段。

**索引**: 
- 主键索引: id
- 唯一索引: username
- 普通索引: email, is_active

#### 2. 角色表 (sys_role)

| 字段名 | 类型 | 长度 | 约束 | 说明 |
|--------|------|------|------|------|
| id | BigAutoField | - | 主键,自增 | 角色唯一标识 |
| name | CharField | 64 | 唯一,非空 | 角色名称 |
| description | CharField | 255 | 可为空 | 角色描述信息 |
| created_at | DateTimeField | - | 自动添加 | 创建时间 |
| updated_at | DateTimeField | - | 自动更新 | 更新时间 |

**用途**: 定义系统中的角色，如管理员、普通用户等。角色是权限的载体，用户通过角色获得权限。

**索引**:
- 主键索引: id  
- 唯一索引: name
- 排序: name ASC

**示例数据**:
```sql
INSERT INTO sys_role (name, description) VALUES 
('超级管理员', '系统最高权限管理员'),
('管理员', '系统管理员'), 
('用户', '普通用户');
```

#### 3. 权限表 (sys_permission)

| 字段名 | 类型 | 长度 | 约束 | 说明 |
|--------|------|------|------|------|
| id | BigAutoField | - | 主键,自增 | 权限唯一标识 |
| name | CharField | 64 | 唯一,非空 | 权限显示名称 |
| codename | CharField | 100 | 唯一,非空 | 权限代码标识 |
| description | CharField | 255 | 可为空 | 权限详细描述 |
| created_at | DateTimeField | - | 自动添加 | 创建时间 |
| updated_at | DateTimeField | - | 自动更新 | 更新时间 |

**用途**: 定义系统中的具体权限，每个权限对应一个或多个功能操作。codename字段用于程序中的权限检查。

**索引**:
- 主键索引: id
- 唯一索引: name, codename  
- 排序: name ASC

**示例数据**:
```sql
INSERT INTO sys_permission (name, codename, description) VALUES
('用户管理', 'manage_users', '管理用户账户'),
('角色管理', 'manage_roles', '管理系统角色'),
('权限管理', 'manage_permissions', '管理系统权限'),
('查看仪表盘', 'view_dashboard', '查看系统仪表盘'),
('系统配置', 'system_config', '修改系统配置');
```

#### 4. 用户角色关联表 (sys_user_role)

| 字段名 | 类型 | 长度 | 约束 | 说明 |
|--------|------|------|------|------|
| id | BigAutoField | - | 主键,自增 | 关联记录唯一标识 |
| user_id | BigIntegerField | - | 外键,非空 | 关联用户ID |
| role_id | BigIntegerField | - | 外键,非空 | 关联角色ID |
| assigned_at | DateTimeField | - | 自动添加 | 角色分配时间 |

**用途**: 建立用户与角色的多对多关系。一个用户可以拥有多个角色，一个角色可以分配给多个用户。

**约束**:
- 外键约束: user_id → auth_user(id), role_id → sys_role(id)
- 唯一约束: (user_id, role_id) 防止重复分配
- 级联删除: 用户或角色删除时，关联记录自动删除

**索引**:
- 主键索引: id
- 唯一索引: (user_id, role_id)
- 外键索引: user_id, role_id
- 排序: user__username ASC, role__name ASC

#### 5. 角色权限关联表 (sys_role_permission)

| 字段名 | 类型 | 长度 | 约束 | 说明 |
|--------|------|------|------|------|
| id | BigAutoField | - | 主键,自增 | 关联记录唯一标识 |
| role_id | BigIntegerField | - | 外键,非空 | 关联角色ID |
| permission_id | BigIntegerField | - | 外键,非空 | 关联权限ID |
| assigned_at | DateTimeField | - | 自动添加 | 权限分配时间 |

**用途**: 建立角色与权限的多对多关系。一个角色可以拥有多个权限，一个权限可以分配给多个角色。

**约束**:
- 外键约束: role_id → sys_role(id), permission_id → sys_permission(id)
- 唯一约束: (role_id, permission_id) 防止重复分配
- 级联删除: 角色或权限删除时，关联记录自动删除

**索引**:
- 主键索引: id
- 唯一索引: (role_id, permission_id)
- 外键索引: role_id, permission_id
- 排序: role__name ASC, permission__name ASC

### 表关系图

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│  auth_user  │────▶│  sys_user_role  │◀────│  sys_role   │
│             │     │                 │     │             │
│ • id (PK)   │     │ • user_id (FK)  │     │ • id (PK)   │
│ • username  │     │ • role_id (FK)  │     │ • name      │
│ • password  │     │ • assigned_at   │     │ • desc...   │
│ • email     │     └─────────────────┘     └─────────────┘
│ • phone     │                                     │
│ • avatar    │                                     ▼
└─────────────┘                             ┌─────────────────────┐
                                            │ sys_role_permission │
                                            │                     │
                                            │ • role_id (FK)      │
                                            │ • permission_id(FK) │
                                            │ • assigned_at       │
                                            └─────────────────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ sys_permission  │
                                            │                 │
                                            │ • id (PK)       │
                                            │ • name          │
                                            │ • codename      │
                                            │ • description   │
                                            └─────────────────┘
```

### RBAC权限检查流程

1. **用户登录** → 获取用户ID
2. **查询用户角色** → 通过 `sys_user_role` 表获取用户的所有角色
3. **查询角色权限** → 通过 `sys_role_permission` 表获取角色的所有权限
4. **权限验证** → 检查用户是否拥有指定的权限代码(codename)

### 数据初始化

系统提供自动初始化脚本 `init_data.sh`，会创建以下默认数据：

**默认角色**:
- 超级管理员: 拥有所有系统权限
- 管理员: 拥有用户管理和仪表盘查看权限  
- 用户: 拥有仪表盘查看权限

**默认权限**:
- manage_users: 用户管理权限
- manage_roles: 角色管理权限
- manage_permissions: 权限管理权限
- view_dashboard: 仪表盘查看权限
- system_config: 系统配置权限

### 性能优化建议

1. **索引优化**:
   - 关联表的外键字段建立索引
   - 经常查询的字段建立索引
   - 复合查询建立复合索引

2. **查询优化**:
   - 使用 `select_related()` 优化外键查询
   - 使用 `prefetch_related()` 优化多对多查询
   - 避免N+1查询问题

3. **缓存策略**:
   - 用户权限信息缓存到Redis
   - 角色权限关系缓存
   - 静态权限数据缓存

### DDL脚本

完整的数据库表结构DDL脚本请参考: `backend/database_schema.sql`

该脚本包含：
- 完整的表结构定义
- 索引创建语句
- 外键约束设置
- 初始化数据插入
- 自动更新时间戳触发器
- 权限查询视图
- 系统统计视图

### 数据库迁移

Django migrations是数据库版本控制系统，**非常重要，不要随意删除**！

#### migrations的作用
- **版本控制**: 记录数据库结构的所有变化历史
- **自动迁移**: Django自动生成SQL语句更新数据库结构
- **团队协作**: 确保所有开发者的数据库结构保持一致
- **回滚功能**: 可以回退到之前的数据库版本

#### migrations目录结构
```
crewaiplatform/migrations/
├── __init__.py              # Python包标识文件（必须保留）
├── 0001_initial.py         # 初始迁移文件
├── 0002_add_fields.py      # 后续迁移文件
└── ...
```

#### 迁移命令
```bash
# 创建迁移文件（检测模型变化）
python manage.py makemigrations crewaiplatform

# 执行迁移（应用到数据库）
python manage.py migrate

# 查看迁移状态
python manage.py showmigrations

# 回退迁移（高级操作）
python manage.py migrate crewaiplatform 0001
```

#### ⚠️ 重要警告
- **__init__.py**: 绝对不能删除
- **生产环境**: 永远不要删除已应用的迁移文件
- **开发环境**: 只有在完全重置时才删除迁移文件
- **团队协作**: 迁移文件需要提交到版本控制系统

使用Django迁移命令创建数据库表：

```bash
# 创建迁移文件
python manage.py makemigrations crewaiplatform

# 执行迁移
python manage.py migrate

# 初始化基础数据
./init_data.sh
```

## 核心功能模块

### 1. 数据模型层 (models.py)
- **User模型**: 扩展Django AbstractUser，添加手机号、头像等字段
- **Role模型**: 系统角色定义，支持角色描述
- **Permission模型**: 系统权限定义，包含权限代码和描述
- **UserRole模型**: 用户与角色多对多关联
- **RolePermission模型**: 角色与权限多对多关联

### 2. 业务逻辑层 (services.py)
- **AuthService**: 认证服务（注册、登录、令牌生成）
- **RBACService**: 权限管理服务（角色分配、权限检查）
- **UserService**: 用户管理服务（用户列表、统计）
- **RoleService**: 角色管理服务
- **PermissionService**: 权限管理服务

### 3. 视图控制层 (views.py)
- **AuthViewSet**: 认证相关API（注册/登录/登出）
- **UserViewSet**: 用户管理 CRUD + 统计接口
- **RoleViewSet**: 角色管理 CRUD + 统计接口
- **PermissionViewSet**: 权限管理 CRUD + 统计接口
- **UserRoleViewSet**: 用户角色关联管理
- **RolePermissionViewSet**: 角色权限关联管理
- **DashboardView**: 仪表盘数据统计接口

### 4. 数据序列化层 (serializers.py)
- **UserRegisterSerializer**: 用户注册数据验证
- **UserSerializer**: 用户信息序列化
- **RoleSerializer**: 角色数据序列化
- **PermissionSerializer**: 权限数据序列化
- **UserRoleSerializer**: 用户角色关联序列化
- **RolePermissionSerializer**: 角色权限关联序列化

## 技术栈

### 后端技术
- **Framework**: Django 4.2+ (单应用架构)
- **API**: Django REST Framework 3.14+
- **Auth**: Django REST Framework SimpleJWT
- **Database**: PostgreSQL (企业级数据库)
- **Cache**: Django-Redis (缓存支持)
- **CORS**: Django-CORS-Headers (跨域支持)

### 前端技术
- **Framework**: Vue 3.5+
- **UI Library**: Element Plus 2.10+
- **Router**: Vue Router 4
- **HTTP**: Axios 1.6+
- **Build Tool**: Vite 7.0+

## 环境配置

### 后端环境变量
```bash
# 数据库配置
DB_NAME=crewai_db
DB_USER=crewai
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Django配置
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# JWT配置
JWT_ACCESS_TOKEN_LIFETIME=60  # 分钟
JWT_REFRESH_TOKEN_LIFETIME=1  # 天

# 跨域配置
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 前端环境变量
```bash
# 开发环境 (.env.development)
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_TITLE=CrewAI Platform (开发环境)

# 生产环境 (.env.production)  
VITE_API_BASE_URL=https://api.crewai-platform.com/api
VITE_APP_TITLE=CrewAI Platform
```

## 快速启动

### 一键启动（推荐）
```bash
# 同时启动前后端服务
./start_all.sh

# 或使用开发工具脚本
./dev.sh start-all
```

### 分别启动
```bash
# 启动后端
cd backend && ./start.sh

# 启动前端（新终端）
cd frontend && ./start.sh
```

### 开发工具脚本
```bash
# 查看所有可用命令
./dev.sh help

# 检查服务状态
./dev.sh status

# 停止所有服务
./dev.sh stop

# 重启服务
./dev.sh restart

# 查看后端日志
./dev.sh logs

# 运行测试
./dev.sh test-backend

# 构建前端
./dev.sh build-frontend

# 重置数据库
./dev.sh reset-db
```

### 初次安装启动
```bash
./scripts/init_backend.sh    # 后端初始化
./scripts/init_frontend.sh   # 前端初始化
```

### 脚本说明

| 脚本名称 | 功能描述 | 使用场景 |
|---------|---------|---------|
| `scripts/init_backend.sh` | 后端完整初始化 | 首次安装或重大更新 |
| `scripts/init_frontend.sh` | 前端完整初始化 | 首次安装或重大更新 |
| `scripts/reset_and_init.sh` | 重置数据库并初始化 | 数据库冲突或完全重置 |
| `scripts/reset_database.sh` | 仅重置数据库 | 清理数据库 |
| `scripts/init_data.sh` | 仅初始化数据 | 重新创建基础数据 |
| `start_all.sh` | 一键启动前后端 | 日常开发启动 |
| `backend/start.sh` | 启动后端服务 | 仅启动后端 |
| `frontend/start.sh` | 启动前端服务 | 仅启动前端 |
| `stop_all.sh` | 停止所有服务 | 停止开发服务器 |
| `dev.sh` | 开发工具集合 | 各种开发操作 |

### 手动启动
**后端**:
```bash
cd backend
pip install -e .
python manage.py makemigrations crewaiplatform
python manage.py migrate
../scripts/init_data.sh  # 初始化基础数据
python manage.py runserver
```

**前端**:
```bash
cd frontend
npm install
npm run dev
```

## API接口文档

### 认证接口
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/logout/` - 用户登出
- `POST /api/auth/refresh/` - 刷新Token
- `GET /api/auth/me/` - 获取当前用户信息

### 数据管理接口
- `GET|POST /api/users/` - 用户列表|创建用户
- `GET /api/users/stats/` - 用户统计信息
- `GET|PUT|DELETE /api/users/{id}/` - 用户详情|更新|删除
- `GET|POST /api/roles/` - 角色列表|创建角色
- `GET /api/roles/stats/` - 角色统计信息
- `GET|PUT|DELETE /api/roles/{id}/` - 角色详情|更新|删除
- `GET|POST /api/permissions/` - 权限列表|创建权限
- `GET /api/permissions/stats/` - 权限统计信息
- `GET|PUT|DELETE /api/permissions/{id}/` - 权限详情|更新|删除
- `GET|POST /api/user-roles/` - 用户角色关联列表|分配角色
- `DELETE /api/user-roles/{id}/` - 移除用户角色
- `GET|POST /api/role-permissions/` - 角色权限关联列表|分配权限
- `DELETE /api/role-permissions/{id}/` - 移除角色权限

### 仪表盘接口
- `GET /api/dashboard/` - 获取仪表盘统计数据

## 数据初始化

项目包含自动数据初始化脚本 `init_data.sh`，会创建：

### 默认角色
- **超级管理员**: 拥有所有权限
- **管理员**: 拥有用户管理和仪表盘查看权限
- **用户**: 拥有仪表盘查看权限

### 默认权限
- **用户管理** (manage_users)
- **角色管理** (manage_roles)
- **权限管理** (manage_permissions)
- **查看仪表盘** (view_dashboard)
- **系统配置** (system_config)

## 开发指南

### Django分层架构说明
1. **models.py**: 数据模型定义，所有数据库表结构
2. **services.py**: 业务逻辑层，封装复杂业务操作
3. **views.py**: 视图控制层，处理HTTP请求响应
4. **serializers.py**: 数据序列化层，API数据验证和转换
5. **admin.py**: Django管理后台配置

### 前端开发规范
- **简化结构**: 去除复杂的目录嵌套
- **API统一管理**: 所有API调用集中在 `services/api.js`
- **状态管理**: 简化的响应式状态管理
- **组件复用**: Element Plus组件库

### 测试命令
```bash
# 后端测试
cd backend
python manage.py test

# 前端构建测试
cd frontend
npm run build
npm run preview
```

## 故障排除

### 数据库迁移问题

#### 问题: "relation 'auth_user' already exists"

这个错误通常出现在数据库中已存在旧版本表结构的情况下。

**错误详情**:
```
django.db.utils.ProgrammingError: relation "auth_user" already exists
```

**解决方案**:

1. **使用数据库重置脚本** (推荐):
   ```bash
   ./scripts/reset_database.sh
   ./scripts/init_backend.sh
   ```

2. **或使用一键重置脚本**:
   ```bash
   ./scripts/reset_and_init.sh
   ```

3. **手动清理** (高级用户):
   ```bash
   # 连接PostgreSQL
   psql -h localhost -U crewai -d postgres
   
   # 删除现有数据库
   DROP DATABASE IF EXISTS crewai_db;
   
   # 创建新数据库
   CREATE DATABASE crewai_db;
   
   # 退出psql
   \q
   
   # 删除旧的迁移文件
   rm -f backend/crewaiplatform/migrations/0*.py
   
   # 重新初始化
   ./scripts/init_backend.sh
   ```

#### 数据库重置脚本说明

**reset_database.sh** 功能:
- 自动删除现有数据库
- 创建新的空数据库
- 清理旧的迁移文件
- 提供安全的数据库重置

**警告**: 数据库重置将删除所有现有数据！

### 常见问题

#### 1. PostgreSQL连接失败
**问题**: 无法连接到PostgreSQL数据库

**解决方案**:
- 确保PostgreSQL服务已启动
- 检查数据库配置（用户名、密码、主机、端口）
- 验证数据库用户权限

#### 2. 端口占用
**问题**: Django服务器端口8000已被占用

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :8000

# 或杀死进程
kill -9 $(lsof -t -i:8000)

# 或使用其他端口启动
python manage.py runserver 0.0.0.0:8001
```

#### 3. 依赖安装失败
**问题**: Python包安装失败

**解决方案**:
```bash
# 升级pip
pip install --upgrade pip

# 清理缓存
pip cache purge

# 重新安装
pip install -e .
```

### 部署检查清单

在部署到生产环境前，请检查：

- [ ] 修改 `DJANGO_SECRET_KEY` 为安全的随机字符串
- [ ] 设置 `DJANGO_DEBUG=False`
- [ ] 配置正确的 `DJANGO_ALLOWED_HOSTS`
- [ ] 使用安全的数据库密码
- [ ] 配置HTTPS相关设置
- [ ] 设置环境变量而非硬编码配置
- [ ] 配置日志文件路径
- [ ] 执行 `collectstatic` 收集静态文件

## 项目特色

### ✅ 重构完成的改进
1. **Django标准架构**: 移除独立应用，采用单应用分层结构
2. **简化目录结构**: 前后端都采用更简洁的目录组织
3. **统一配置管理**: 环境变量驱动的配置方式
4. **自动数据初始化**: 一键创建基础角色权限数据
5. **完善的注释**: 每个模块都有详细的功能说明
6. **动态数据展示**: 真实API驱动的仪表盘

### 🚀 架构优势
- **简单明了**: Django单应用架构，易于理解和维护
- **标准规范**: 遵循Django最佳实践
- **开发效率**: 减少了复杂的应用间依赖
- **部署友好**: 单一应用，部署更简单
- **扩展性好**: 基于服务层的设计便于功能扩展

这是一个采用Django标准分层架构的企业级权限管理系统，结构清晰、易于维护，适合作为权限管理系统的基础框架。
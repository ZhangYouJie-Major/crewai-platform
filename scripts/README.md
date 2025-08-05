# CrewAI Platform 脚本说明

此目录包含 CrewAI Platform 项目的核心管理脚本。

## 脚本列表

### 🚀 初始化脚本
- **`init_backend.sh`** - 后端完整初始化
  - 检查 Python 版本和依赖
  - 执行数据库迁移
  - 初始化基础数据
  - 启动 Django 服务器

- **`init_frontend.sh`** - 前端完整初始化
  - 检查 Node.js 版本
  - 安装 npm 依赖
  - 启动 Vue 开发服务器

### 📊 数据初始化脚本
- **`init_data.sh`** - 数据库基础数据初始化
  - 创建默认角色（超级管理员、管理员、用户）
  - 创建默认权限
  - 分配角色权限关系

- **`init_crewai_data.sh`** - CrewAI 基础数据初始化
  - 创建 LLM 模型配置
  - 创建 MCP 工具配置

- **`init_dictionary_data.sh`** - 字典数据初始化
  - 创建基础字典数据
  - 建立字典层级关系

### 🔄 重置脚本
- **`reset_database.sh`** - 数据库重置
  - 删除现有数据库
  - 创建新的空数据库
  - 清理迁移文件

- **`reset_and_init.sh`** - 一键重置并初始化
  - 执行数据库重置
  - 重新初始化后端

## 使用方法

### 首次安装
```bash
# 从项目根目录执行
./scripts/init_backend.sh    # 初始化后端
./scripts/init_frontend.sh   # 初始化前端
```

### 数据库问题修复
```bash
# 重置数据库并重新初始化
./scripts/reset_and_init.sh
```

### 仅重置数据库
```bash
./scripts/reset_database.sh
```

### 初始化特定数据
```bash
# 初始化基础数据
./scripts/init_data.sh

# 初始化 CrewAI 数据
./scripts/init_crewai_data.sh

# 初始化字典数据
./scripts/init_dictionary_data.sh
```

## 注意事项

1. **权限要求**: 所有脚本都需要执行权限
2. **路径依赖**: 脚本使用相对路径，请从项目根目录调用
3. **数据安全**: 重置脚本会删除所有数据，请谨慎使用
4. **环境变量**: 支持通过环境变量自定义配置

## 环境变量配置

```bash
# 数据库配置
export DB_NAME=crewai_db
export DB_USER=crewai
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432

# Django 配置
export DJANGO_DEBUG=True
export CREATE_SUPERUSER=true
export SUPERUSER_USERNAME=admin
export SUPERUSER_EMAIL=admin@example.com
``` 
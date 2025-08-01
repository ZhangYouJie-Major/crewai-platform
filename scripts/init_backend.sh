#!/bin/bash

# CrewAI Platform 后端初始化脚本
# 用于初始化Django后端环境和启动服务

set -e  # 遇到错误立即退出

echo "========================================="
echo "CrewAI Platform 后端环境初始化开始..."
echo "========================================="

# 切换到项目的backend目录
cd "$(dirname "$0")/../backend"

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要Python $required_version 或更高版本，当前版本: $python_version"
    exit 1
fi

echo "Python版本检查通过: $python_version"

# 创建日志目录
echo "创建日志目录..."
mkdir -p logs

# 安装Python依赖
echo "安装Python依赖包..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install -e .
fi

# 检查PostgreSQL连接（可选）
echo "检查数据库连接..."
if command -v psql &> /dev/null; then
    # 如果psql可用，测试连接
    DB_NAME=${DB_NAME:-crewai_db}
    DB_USER=${DB_USER:-crewai}
    DB_HOST=${DB_HOST:-localhost}
    DB_PORT=${DB_PORT:-5432}
    
    if PGPASSWORD=${DB_PASSWORD:-123456} psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; then
        echo "数据库连接成功"
    else
        echo "警告: 无法连接到数据库，请确保PostgreSQL已启动并配置正确"
        echo "数据库配置: $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
    fi
else
    echo "跳过数据库连接检查（未安装psql）"
fi

# 运行数据库迁移
echo "执行数据库迁移..."
python manage.py makemigrations crewaiplatform

# 尝试执行迁移，如果失败则提示重置数据库
if ! python manage.py migrate 2>/dev/null; then
    echo ""
    echo "========================================="
    echo "数据库迁移失败！"
    echo "检测到数据库中存在冲突的表结构。"
    echo "这通常是因为数据库中存在旧版本的表。"
    echo ""
    echo "解决方案："
    echo "1. 运行数据库重置脚本："
    echo "   ./reset_database.sh"
    echo "2. 然后重新运行此脚本："
    echo "   ./init_backend.sh"
    echo ""
    echo "警告：重置数据库将删除所有现有数据！"
    echo "========================================="
    exit 1
fi

# 初始化基础数据
echo "初始化基础数据..."
if [ -f "../scripts/init_data.sh" ]; then
    ../scripts/init_data.sh
else
    echo "警告: 未找到数据初始化脚本"
fi

# 创建超级用户（可选）
echo "检查是否需要创建超级用户..."
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "创建超级用户..."
    python manage.py createsuperuser --noinput --username ${SUPERUSER_USERNAME:-admin} --email ${SUPERUSER_EMAIL:-admin@example.com} || true
fi

# 收集静态文件（生产环境）
if [ "$DJANGO_DEBUG" = "False" ] || [ "$DJANGO_DEBUG" = "false" ]; then
    echo "收集静态文件..."
    python manage.py collectstatic --noinput
fi

echo "========================================="
echo "后端初始化完成！"
echo "========================================="

# 启动Django开发服务器
echo "启动Django开发服务器..."
echo "服务器地址: http://localhost:8000"
echo "API文档: http://localhost:8000/api/"
echo "管理后台: http://localhost:8000/admin/"
echo "========================================="

# 设置默认的主机和端口
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}

python manage.py runserver "$HOST:$PORT" 
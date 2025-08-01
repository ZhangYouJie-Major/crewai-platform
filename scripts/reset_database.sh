#!/bin/bash

# CrewAI Platform 数据库重置脚本
# 用于清理旧数据库结构并重新初始化

set -e  # 遇到错误立即退出

echo "========================================="
echo "重置CrewAI Platform数据库..."
echo "========================================="

# 获取数据库配置
DB_NAME=${DB_NAME:-crewai_db}
DB_USER=${DB_USER:-crewai}
DB_PASSWORD=${DB_PASSWORD:-123456}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}

echo "数据库配置: $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"

# 检查psql是否可用
if ! command -v psql &> /dev/null; then
    echo "错误: 未找到psql命令，请确保PostgreSQL客户端已安装"
    exit 1
fi

# 删除现有数据库（如果存在）
echo "删除现有数据库..."
PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || {
    echo "警告: 无法删除数据库，可能数据库不存在或权限不足"
}

# 创建新数据库
echo "创建新数据库..."
PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;" || {
    echo "错误: 无法创建数据库"
    exit 1
}

echo "数据库重置完成！"

# 删除现有的迁移文件（除了__init__.py）
echo "清理旧的迁移文件..."
echo "⚠️  警告: 即将删除所有迁移文件（保留__init__.py）"
BACKEND_DIR="$(dirname "$0")/../backend"
if [ -d "$BACKEND_DIR/crewaiplatform/migrations" ]; then
    # 只删除数字开头的迁移文件，保留__init__.py
    find "$BACKEND_DIR/crewaiplatform/migrations" -name "0*.py" -delete
    echo "已删除旧的迁移文件，保留migrations目录和__init__.py"
else
    echo "migrations目录不存在，将在迁移时自动创建"
fi

echo "========================================="
echo "数据库重置脚本执行完成！"
echo "现在可以运行 init_backend.sh 进行重新初始化"
echo "========================================="
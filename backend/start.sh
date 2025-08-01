#!/bin/bash

# CrewAI Platform 后端启动脚本
# 用于日常开发中快速启动Django服务器

set -e  # 遇到错误立即退出

echo "========================================="
echo "启动CrewAI Platform后端服务..."
echo "========================================="

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查虚拟环境（可选）
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 检查依赖是否安装
if [ ! -f ".dependencies_installed" ]; then
    echo "检测到首次运行，安装依赖..."
    pip install -e .
    touch .dependencies_installed
fi

# 快速数据库检查
echo "检查数据库连接..."
if ! python manage.py check --database default 2>/dev/null; then
    echo "数据库连接失败，请检查数据库配置"
    echo "如需初始化数据库，请运行: ./init_backend.sh"
    exit 1
fi

# 检查是否需要迁移
if python manage.py showmigrations --plan 2>/dev/null | grep -q "\[ \]"; then
    echo "检测到未应用的迁移，正在应用..."
    python manage.py migrate
fi

# 创建日志目录
mkdir -p logs

# 设置默认的主机和端口
HOST=${HOST:-127.0.0.1}
PORT=${PORT:-8000}

echo "========================================="
echo "Django服务器启动信息:"
echo "服务器地址: http://$HOST:$PORT"
echo "API文档: http://$HOST:$PORT/api/"
echo "管理后台: http://$HOST:$PORT/admin/"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "========================================="

# 启动Django开发服务器
python manage.py runserver "$HOST:$PORT"
#!/bin/bash

# CrewAI Platform WebSocket支持的启动脚本
# 使用Daphne ASGI服务器以支持WebSocket连接

echo "========================================="
echo "启动CrewAI Platform WebSocket服务..."
echo "========================================="

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查虚拟环境（可选）
if [ -d ".venv" ]; then
    echo "激活虚拟环境..."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 检查并安装依赖
echo "检查依赖..."
pip install -e . -q

# 检查数据库连接
echo "检查数据库连接..."
CHECK_OUTPUT=$(python manage.py check --database default 2>&1)
CHECK_EXIT_CODE=$?
if [ $CHECK_EXIT_CODE -eq 0 ]; then
    echo "数据库连接正常"
else
    echo "数据库检查输出: $CHECK_OUTPUT"
    echo "数据库连接失败，请检查数据库配置"
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
echo "ASGI服务器启动信息:"
echo "服务器地址: http://$HOST:$PORT"
echo "WebSocket地址: ws://$HOST:$PORT/ws/"
echo "API文档: http://$HOST:$PORT/api/"
echo "管理后台: http://$HOST:$PORT/admin/"
echo ""
echo "WebSocket路由:"
echo "  - ws://$HOST:$PORT/ws/chat/<conversation_id>/"
echo "  - ws://$HOST:$PORT/ws/notifications/"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "========================================="

# 使用Daphne启动ASGI服务器（支持WebSocket）
daphne -b "$HOST" -p "$PORT" crewaiplatform.asgi:application
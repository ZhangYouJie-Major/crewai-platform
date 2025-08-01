#!/bin/bash

# CrewAI Platform 一键启动脚本
# 同时启动前后端服务，用于日常开发

set -e

echo "========================================="
echo "CrewAI Platform 一键启动..."
echo "========================================="

# 检查系统是否支持并行启动
if ! command -v trap &> /dev/null; then
    echo "警告: 系统不支持信号处理，将依次启动服务"
    PARALLEL_MODE=false
else
    PARALLEL_MODE=true
fi

# 定义清理函数
cleanup() {
    echo ""
    echo "正在停止所有服务..."
    
    # 杀死所有子进程
    if [ "$PARALLEL_MODE" = true ]; then
        jobs -p | xargs -r kill 2>/dev/null || true
    fi
    
    echo "所有服务已停止"
    exit 0
}

# 设置信号处理
if [ "$PARALLEL_MODE" = true ]; then
    trap cleanup SIGINT SIGTERM
fi

# 启动后端服务
start_backend() {
    echo "启动后端服务..."
    cd backend
    ./start.sh
}

# 启动前端服务
start_frontend() {
    echo "启动前端服务..."
    cd frontend
    ./start.sh
}

# 根据模式启动服务
if [ "$PARALLEL_MODE" = true ]; then
    echo "使用并行模式启动前后端服务..."
    echo "按 Ctrl+C 停止所有服务"
    echo ""
    
    # 在后台启动后端
    start_backend &
    BACKEND_PID=$!
    
    # 等待后端启动
    sleep 3
    
    # 在后台启动前端
    start_frontend &
    FRONTEND_PID=$!
    
    echo "========================================="
    echo "服务启动完成!"
    echo "后端服务: http://127.0.0.1:8000"
    echo "前端服务: http://localhost:5173"
    echo "========================================="
    
    # 等待子进程
    wait
else
    echo "使用顺序模式启动服务..."
    echo "请手动在另一个终端运行前端服务"
    echo ""
    
    start_backend
fi
#!/bin/bash

# CrewAI Platform 停止所有服务脚本

echo "========================================="
echo "停止CrewAI Platform所有服务..."
echo "========================================="

# 停止占用8000端口的进程（Django后端）
echo "停止后端服务..."
BACKEND_PIDS=$(lsof -t -i:8000 2>/dev/null || true)
if [ -n "$BACKEND_PIDS" ]; then
    echo "发现后端进程: $BACKEND_PIDS"
    kill -TERM $BACKEND_PIDS 2>/dev/null || true
    sleep 2
    # 如果进程仍在运行，强制杀死
    BACKEND_PIDS=$(lsof -t -i:8000 2>/dev/null || true)
    if [ -n "$BACKEND_PIDS" ]; then
        echo "强制停止后端进程: $BACKEND_PIDS"
        kill -KILL $BACKEND_PIDS 2>/dev/null || true
    fi
    echo "后端服务已停止"
else
    echo "未发现运行中的后端服务"
fi

# 停止占用5173端口的进程（Vue前端）
echo "停止前端服务..."
FRONTEND_PIDS=$(lsof -t -i:5173 2>/dev/null || true)
if [ -n "$FRONTEND_PIDS" ]; then
    echo "发现前端进程: $FRONTEND_PIDS"
    kill -TERM $FRONTEND_PIDS 2>/dev/null || true
    sleep 2
    # 如果进程仍在运行，强制杀死
    FRONTEND_PIDS=$(lsof -t -i:5173 2>/dev/null || true)
    if [ -n "$FRONTEND_PIDS" ]; then
        echo "强制停止前端进程: $FRONTEND_PIDS"
        kill -KILL $FRONTEND_PIDS 2>/dev/null || true
    fi
    echo "前端服务已停止"
else
    echo "未发现运行中的前端服务"
fi

# 清理可能的npm和python进程
echo "清理相关进程..."
pkill -f "python.*manage.py.*runserver" 2>/dev/null || true
pkill -f "npm.*run.*dev" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

echo "========================================="
echo "所有服务已停止！"
echo "========================================="
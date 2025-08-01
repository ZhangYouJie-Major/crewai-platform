#!/bin/bash

# CrewAI Platform 前端启动脚本
# 用于日常开发中快速启动Vue开发服务器

set -e  # 遇到错误立即退出

echo "========================================="
echo "启动CrewAI Platform前端服务..."
echo "========================================="

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查Node.js版本
echo "检查Node.js版本..."
if ! command -v node &> /dev/null; then
    echo "错误: 未安装Node.js，请先安装Node.js 16+"
    exit 1
fi

node_version=$(node --version | sed 's/v//')
required_version="16.0.0"

if [ "$(printf '%s\n' "$required_version" "$node_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要Node.js $required_version 或更高版本，当前版本: $node_version"
    exit 1
fi

echo "Node.js版本检查通过: $node_version"

# 检查依赖是否安装
if [ ! -d "node_modules" ] || [ ! -f ".dependencies_installed" ]; then
    echo "检测到首次运行或依赖缺失，安装依赖..."
    npm install
    touch .dependencies_installed
fi

# 设置默认的主机和端口
HOST=${HOST:-localhost}
PORT=${PORT:-5173}

echo "========================================="
echo "Vue开发服务器启动信息:"
echo "前端地址: http://$HOST:$PORT"
echo "网络地址: http://$(hostname -I | awk '{print $1}'):$PORT"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "========================================="

# 启动Vue开发服务器
npm run dev -- --host "$HOST" --port "$PORT"
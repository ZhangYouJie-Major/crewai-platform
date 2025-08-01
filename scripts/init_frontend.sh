#!/bin/bash

# CrewAI Platform 前端初始化脚本
# 用于初始化Vue.js前端环境和启动开发服务器

set -e  # 遇到错误立即退出

echo "========================================="
echo "CrewAI Platform 前端环境初始化开始..."
echo "========================================="

# 切换到项目的frontend目录
cd "$(dirname "$0")/../frontend"

# 检查Node.js版本
echo "检查Node.js版本..."
if ! command -v node &> /dev/null; then
    echo "错误: 未安装Node.js，请先安装Node.js 16或更高版本"
    exit 1
fi

node_version=$(node --version | grep -oE '[0-9]+' | head -1)
if [ "$node_version" -lt 16 ]; then
    echo "错误: 需要Node.js 16或更高版本，当前版本: $(node --version)"
    exit 1
fi

echo "Node.js版本检查通过: $(node --version)"

# 检查npm版本
echo "检查npm版本..."
if ! command -v npm &> /dev/null; then
    echo "错误: 未安装npm包管理器"
    exit 1
fi

echo "npm版本: $(npm --version)"

# 清理node_modules（可选）
if [ "$CLEAN_INSTALL" = "true" ]; then
    echo "清理现有依赖..."
    rm -rf node_modules
    rm -f package-lock.json
fi

# 安装依赖包
echo "安装前端依赖包..."
if [ -f "package-lock.json" ]; then
    npm ci  # 使用ci进行清洁安装
else
    npm install
fi

# 检查必要的依赖
echo "检查关键依赖..."
required_deps=("vue" "element-plus" "axios" "vue-router")
for dep in "${required_deps[@]}"; do
    if npm list "$dep" &> /dev/null; then
        echo "✓ $dep 已安装"
    else
        echo "✗ 缺少依赖: $dep"
        echo "正在安装 $dep..."
        npm install "$dep"
    fi
done

# 检查环境配置文件
echo "检查环境配置..."
if [ ! -f ".env" ]; then
    echo "创建默认环境配置文件..."
    cat > .env << EOF
# CrewAI Platform 前端环境配置
VITE_APP_TITLE=CrewAI Platform
VITE_API_BASE_URL=/api
EOF
fi

if [ ! -f ".env.development" ]; then
    echo "创建开发环境配置文件..."
    cat > .env.development << EOF
# 开发环境配置
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_TITLE=CrewAI Platform (开发环境)
VITE_APP_ENV=development
EOF
fi

# 运行代码检查（如果配置了）
if npm run lint --silent &> /dev/null; then
    echo "运行代码检查..."
    npm run lint || echo "警告: 代码检查发现问题，但继续启动服务"
fi

# 构建项目（可选，用于检查编译错误）
if [ "$BUILD_CHECK" = "true" ]; then
    echo "检查项目构建..."
    npm run build
fi

echo "========================================="
echo "前端初始化完成！"
echo "========================================="

# 启动Vite开发服务器
echo "启动Vite开发服务器..."
echo "前端地址: http://localhost:5173"
echo "后端API: ${VITE_API_BASE_URL:-http://localhost:8000/api}"
echo "========================================="
echo ""
echo "提示:"
echo "- 请确保后端服务已启动 (端口8000)"
echo "- 如需更改端口，请设置环境变量 PORT"
echo "- 按 Ctrl+C 停止服务"
echo ""

# 设置端口（如果指定）
if [ -n "$PORT" ]; then
    echo "使用自定义端口: $PORT"
    npm run dev -- --port "$PORT"
else
    npm run dev
fi 
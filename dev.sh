#!/bin/bash

# CrewAI Platform 开发工具脚本集合

show_help() {
    echo "CrewAI Platform 开发工具"
    echo ""
    echo "用法: ./dev.sh [命令]"
    echo ""
    echo "可用命令:"
    echo "  start-backend    启动后端服务"
    echo "  start-frontend   启动前端服务"
    echo "  start-all        同时启动前后端服务"
    echo "  stop             停止所有服务"
    echo "  restart          重启所有服务"
    echo "  status           检查服务状态"
    echo "  logs             查看后端日志"
    echo "  test-backend     运行后端测试"
    echo "  test-frontend    运行前端测试"
    echo "  build-frontend   构建前端项目"
    echo "  reset-db         重置数据库"
    echo "  help             显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./dev.sh start-all     # 启动前后端服务"
    echo "  ./dev.sh status        # 检查服务状态"
    echo "  ./dev.sh reset-db      # 重置数据库"
}

check_status() {
    echo "========================================="
    echo "CrewAI Platform 服务状态"
    echo "========================================="
    
    # 检查后端服务
    if lsof -i:8000 &>/dev/null; then
        BACKEND_PID=$(lsof -t -i:8000)
        echo "✅ 后端服务: 运行中 (PID: $BACKEND_PID, 端口: 8000)"
        echo "   访问地址: http://127.0.0.1:8000"
    else
        echo "❌ 后端服务: 未运行"
    fi
    
    # 检查前端服务
    if lsof -i:5173 &>/dev/null; then
        FRONTEND_PID=$(lsof -t -i:5173)
        echo "✅ 前端服务: 运行中 (PID: $FRONTEND_PID, 端口: 5173)"
        echo "   访问地址: http://localhost:5173"
    else
        echo "❌ 前端服务: 未运行"
    fi
    
    # 检查数据库连接
    echo ""
    echo "数据库连接状态:"
    cd backend
    if python manage.py check --database default 2>/dev/null; then
        echo "✅ 数据库: 连接正常"
    else
        echo "❌ 数据库: 连接失败"
    fi
    cd ..
}

show_logs() {
    echo "========================================="
    echo "查看后端日志 (按 Ctrl+C 退出)"
    echo "========================================="
    
    if [ -f "backend/logs/django.log" ]; then
        tail -f backend/logs/django.log
    else
        echo "日志文件不存在，启动后端服务后会生成日志文件"
    fi
}

# 主逻辑
case "${1:-help}" in
    "start-backend")
        cd backend && ./start.sh
        ;;
    "start-frontend")
        cd frontend && ./start.sh
        ;;
    "start-all")
        ./start_all.sh
        ;;
    "stop")
        ./stop_all.sh
        ;;
    "restart")
        echo "重启所有服务..."
        ./stop_all.sh
        sleep 2
        ./start_all.sh
        ;;
    "status")
        check_status
        ;;
    "logs")
        show_logs
        ;;
    "test-backend")
        echo "运行后端测试..."
        cd backend
        python manage.py test
        ;;
    "test-frontend")
        echo "运行前端测试..."
        cd frontend
        npm run test 2>/dev/null || echo "前端测试脚本未配置"
        ;;
    "build-frontend")
        echo "构建前端项目..."
        cd frontend
        npm run build
        ;;
    "reset-db")
        echo "重置数据库..."
        ./scripts/reset_database.sh
        ./scripts/init_backend.sh
        ;;
    "help"|*)
        show_help
        ;;
esac
#!/usr/bin/env python3
"""
WebSocket功能测试运行器

运行所有WebSocket相关的功能测试:
1. 配置和依赖检查
2. 流式对话集成测试
"""

import sys
import subprocess
from pathlib import Path

def run_functionality_test():
    """运行功能测试"""
    print("🔧 运行WebSocket功能测试...")
    print("=" * 50)
    
    test_file = Path(__file__).parent / "test_websocket_functionality.py"
    
    try:
        result = subprocess.run([
            sys.executable, str(test_file)
        ], capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ 功能测试超时")
        return False
    except Exception as e:
        print(f"❌ 功能测试运行失败: {e}")
        return False

def run_integration_test():
    """运行集成测试"""
    print("\n💬 运行流式对话集成测试...")
    print("=" * 50)
    
    test_file = Path(__file__).parent / "test_streaming_integration.py"
    
    print("⚠️ 注意: 集成测试需要ASGI服务器运行")
    print("   请先启动: ./backend/start_websocket.sh")
    
    user_input = input("\n是否继续集成测试? (y/N): ").strip().lower()
    if user_input not in ['y', 'yes']:
        print("跳过集成测试")
        return True
    
    try:
        result = subprocess.run([
            sys.executable, str(test_file)
        ], timeout=60)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ 集成测试超时")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ 集成测试被用户中断")
        return False
    except Exception as e:
        print(f"❌ 集成测试运行失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 WebSocket流式对话功能测试套件")
    print("=" * 60)
    
    # 运行功能测试
    functionality_passed = run_functionality_test()
    
    # 运行集成测试
    integration_passed = run_integration_test()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试套件总结")
    print("=" * 60)
    
    print(f"功能测试: {'✅ 通过' if functionality_passed else '❌ 失败'}")
    print(f"集成测试: {'✅ 通过' if integration_passed else '❌ 失败'}")
    
    if functionality_passed and integration_passed:
        print("\n🎉 所有测试通过!")
        print("💡 WebSocket流式对话功能已就绪")
        print("🌐 现在可以在前端界面体验完整功能")
    else:
        print("\n🔧 部分测试失败，请检查:")
        if not functionality_passed:
            print("   - Django配置和依赖")
            print("   - 数据库连接和数据")
        if not integration_passed:
            print("   - ASGI服务器是否运行")
            print("   - WebSocket连接配置")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
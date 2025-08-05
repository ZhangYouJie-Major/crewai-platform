#!/usr/bin/env python3
"""
统一测试执行脚本
支持选择性运行测试和生成测试报告
"""

import sys
import time
import argparse
from datetime import datetime
from typing import Dict, List, Any

# 导入所有测试类
from test_auth import AuthTester
from test_agent_management import AgentManagementTester
from test_mcp_tool_management import MCPToolManagementTester
from test_dictionary_management import DictionaryManagementTester

class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.test_suites = {
            "auth": {
                "name": "认证测试",
                "class": AuthTester,
                "description": "登录、登出、Token验证等认证相关测试"
            },
            "agent": {
                "name": "Agent管理测试",
                "class": AgentManagementTester,
                "description": "Agent的CRUD操作、克隆、启用/禁用等功能测试"
            },
            "mcp": {
                "name": "MCP工具管理测试",
                "class": MCPToolManagementTester,
                "description": "MCP工具的CRUD操作、健康检查等功能测试"
            },
            "dictionary": {
                "name": "字典管理测试",
                "class": DictionaryManagementTester,
                "description": "字典的CRUD操作、树结构、父子关系等功能测试"
            }
        }
        
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def list_tests(self):
        """列出所有可用的测试套件"""
        print("📋 可用的测试套件:")
        print("=" * 60)
        
        for key, suite in self.test_suites.items():
            print(f"🔑 {key:12} - {suite['name']}")
            print(f"   描述: {suite['description']}")
            print()
        
        print("💡 使用方法:")
        print("   python run_tests.py --suite auth")
        print("   python run_tests.py --suite auth,agent")
        print("   python run_tests.py --all")
        print()
    
    def run_single_suite(self, suite_key: str) -> Dict[str, Any]:
        """运行单个测试套件"""
        if suite_key not in self.test_suites:
            print(f"❌ 未知的测试套件: {suite_key}")
            return {"success": False, "error": f"未知的测试套件: {suite_key}"}
        
        suite = self.test_suites[suite_key]
        print(f"🚀 开始运行 {suite['name']}...")
        print(f"📝 {suite['description']}")
        print("-" * 60)
        
        try:
            tester = suite["class"]()
            success = tester.run_all_tests()
            
            result = {
                "success": success,
                "passed": tester.test_results["passed"],
                "failed": tester.test_results["failed"],
                "errors": tester.test_results["errors"],
                "total": tester.test_results["passed"] + tester.test_results["failed"]
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 运行测试套件 {suite_key} 时发生异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "passed": 0,
                "failed": 1,
                "total": 1
            }
    
    def run_multiple_suites(self, suite_keys: List[str]) -> Dict[str, Any]:
        """运行多个测试套件"""
        print(f"🚀 开始运行 {len(suite_keys)} 个测试套件...")
        print("=" * 60)
        
        results = {}
        total_passed = 0
        total_failed = 0
        total_errors = []
        
        for suite_key in suite_keys:
            print(f"\n📦 测试套件: {suite_key}")
            result = self.run_single_suite(suite_key)
            results[suite_key] = result
            
            total_passed += result.get("passed", 0)
            total_failed += result.get("failed", 0)
            if "errors" in result:
                total_errors.extend(result["errors"])
        
        overall_success = total_failed == 0
        
        return {
            "success": overall_success,
            "results": results,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_errors": total_errors,
            "total_tests": total_passed + total_failed
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试套件"""
        return self.run_multiple_suites(list(self.test_suites.keys()))
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成测试报告"""
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        report = []
        report.append("=" * 80)
        report.append("📊 CrewAI Platform 测试报告")
        report.append("=" * 80)
        report.append(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"⏱️  总耗时: {duration:.2f} 秒")
        report.append(f"🎯 总体结果: {'✅ 通过' if results['success'] else '❌ 失败'}")
        report.append("")
        
        if "results" in results:
            # 多个测试套件的结果
            report.append("📋 详细结果:")
            report.append("-" * 60)
            
            for suite_key, result in results["results"].items():
                suite_name = self.test_suites[suite_key]["name"]
                status = "✅ 通过" if result["success"] else "❌ 失败"
                report.append(f"🔑 {suite_name:20} - {status}")
                report.append(f"   通过: {result.get('passed', 0):3d}, 失败: {result.get('failed', 0):3d}")
                
                if "errors" in result and result["errors"]:
                    report.append(f"   错误: {len(result['errors'])} 个")
            
            report.append("")
            report.append("📊 汇总统计:")
            report.append(f"   总测试数: {results['total_tests']}")
            report.append(f"   通过数: {results['total_passed']}")
            report.append(f"   失败数: {results['total_failed']}")
            report.append(f"   成功率: {(results['total_passed']/results['total_tests']*100):.1f}%" if results['total_tests'] > 0 else "0%")
            
            if results["total_errors"]:
                report.append("")
                report.append("❌ 错误详情:")
                for error in results["total_errors"]:
                    report.append(f"   - {error}")
        else:
            # 单个测试套件的结果
            report.append(f"📋 测试结果:")
            report.append(f"   通过: {results.get('passed', 0)}")
            report.append(f"   失败: {results.get('failed', 0)}")
            report.append(f"   总数: {results.get('total', 0)}")
            
            if "errors" in results and results["errors"]:
                report.append("")
                report.append("❌ 错误详情:")
                for error in results["errors"]:
                    report.append(f"   - {error}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, report: str, filename: str = None):
        """保存测试报告到文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.txt"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"📄 测试报告已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存测试报告失败: {str(e)}")
    
    def run(self, args):
        """运行测试"""
        self.start_time = time.time()
        
        if args.list:
            self.list_tests()
            return
        
        if args.all:
            print("🚀 运行所有测试套件...")
            results = self.run_all_tests()
        elif args.suite:
            suite_keys = [key.strip() for key in args.suite.split(",")]
            results = self.run_multiple_suites(suite_keys)
        else:
            print("❌ 请指定要运行的测试套件")
            print("💡 使用 --help 查看帮助信息")
            return
        
        # 生成报告
        report = self.generate_report(results)
        print("\n" + report)
        
        # 保存报告
        if args.save_report:
            self.save_report(report, args.output)
        
        # 返回退出码
        sys.exit(0 if results["success"] else 1)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="CrewAI Platform 测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python run_tests.py --list                    # 列出所有测试套件
  python run_tests.py --suite auth              # 运行认证测试
  python run_tests.py --suite auth,agent        # 运行认证和Agent管理测试
  python run_tests.py --all                     # 运行所有测试
  python run_tests.py --all --save-report       # 运行所有测试并保存报告
  python run_tests.py --suite auth --output auth_report.txt  # 指定输出文件
        """
    )
    
    parser.add_argument(
        "--list", 
        action="store_true",
        help="列出所有可用的测试套件"
    )
    
    parser.add_argument(
        "--suite",
        type=str,
        help="指定要运行的测试套件 (用逗号分隔多个套件)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="运行所有测试套件"
    )
    
    parser.add_argument(
        "--save-report",
        action="store_true",
        help="保存测试报告到文件"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="指定测试报告输出文件名"
    )
    
    args = parser.parse_args()
    
    # 验证参数
    if not any([args.list, args.suite, args.all]):
        parser.print_help()
        return
    
    if args.suite and args.all:
        print("❌ 不能同时使用 --suite 和 --all 参数")
        return
    
    # 运行测试
    runner = TestRunner()
    runner.run(args)

if __name__ == "__main__":
    main() 
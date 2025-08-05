#!/usr/bin/env python3
"""
测试基类
提供通用的测试工具和方法
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# 添加Django项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crewaiplatform.settings')

import django
django.setup()

from test_config import API_BASE_URL, TEST_ACCOUNTS, API_ENDPOINTS, TIMEOUT, LOG_LEVEL, LOG_FORMAT

class BaseTester:
    """测试基类，提供通用的测试功能"""
    
    def __init__(self, test_name: str = "BaseTest"):
        self.test_name = test_name
        self.base_url = API_BASE_URL
        self.token = None
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        
        # 设置日志
        self._setup_logging()
        
        # 测试结果记录
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def _setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format=LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f"test_{self.test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            ]
        )
        self.logger = logging.getLogger(self.test_name)
    
    def authenticate(self, account_type: str = "admin") -> bool:
        """认证获取Token"""
        try:
            if account_type not in TEST_ACCOUNTS:
                self.logger.error(f"未知的账号类型: {account_type}")
                return False
            
            account = TEST_ACCOUNTS[account_type]
            login_data = {
                "username": account["username"],
                "password": account["password"]
            }
            
            self.logger.info(f"正在使用账号 {account['username']} 进行认证...")
            
            response = self.session.post(
                f"{self.base_url}{API_ENDPOINTS['auth']['login']}", 
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access')
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                self.logger.info("✅ 认证成功")
                return True
            else:
                self.logger.error(f"❌ 认证失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ 认证异常: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """获取认证头"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    params: Optional[Dict] = None) -> Tuple[int, Dict]:
        """发送HTTP请求"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            return response.status_code, response.json() if response.content else {}
            
        except Exception as e:
            self.logger.error(f"请求异常: {str(e)}")
            return 500, {"error": str(e)}
    
    def assert_status_code(self, status_code: int, expected: int, message: str = "") -> bool:
        """断言状态码"""
        if status_code == expected:
            self.logger.info(f"✅ {message} - 状态码: {status_code}")
            self.test_results["passed"] += 1
            return True
        else:
            self.logger.error(f"❌ {message} - 期望状态码: {expected}, 实际状态码: {status_code}")
            self.test_results["failed"] += 1
            return False
    
    def assert_response_contains(self, response: Dict, key: str, message: str = "") -> bool:
        """断言响应包含指定键"""
        if key in response:
            self.logger.info(f"✅ {message} - 包含键: {key}")
            self.test_results["passed"] += 1
            return True
        else:
            self.logger.error(f"❌ {message} - 缺少键: {key}")
            self.test_results["failed"] += 1
            return False
    
    def assert_response_value(self, response: Dict, key: str, expected_value: Any, message: str = "") -> bool:
        """断言响应中指定键的值"""
        if key in response and response[key] == expected_value:
            self.logger.info(f"✅ {message} - {key}: {expected_value}")
            self.test_results["passed"] += 1
            return True
        else:
            actual_value = response.get(key, "NOT_FOUND")
            self.logger.error(f"❌ {message} - 期望 {key}: {expected_value}, 实际: {actual_value}")
            self.test_results["failed"] += 1
            return False
    
    def create_test_data(self, data_type: str, **kwargs) -> Dict:
        """创建测试数据"""
        from test_config import TEST_DATA
        
        if data_type not in TEST_DATA:
            raise ValueError(f"未知的数据类型: {data_type}")
        
        test_data = TEST_DATA[data_type].copy()
        test_data.update(kwargs)
        
        # 添加时间戳避免重复
        if "name" in test_data:
            test_data["name"] = f"{test_data['name']}_{int(time.time())}"
        
        return test_data
    
    def cleanup_test_data(self, endpoint: str, item_id: int) -> bool:
        """清理测试数据"""
        try:
            status_code, response = self.make_request("DELETE", f"{endpoint}{item_id}/")
            if status_code in [200, 204]:
                self.logger.info(f"✅ 清理测试数据成功: {endpoint}{item_id}/")
                return True
            else:
                self.logger.warning(f"⚠️ 清理测试数据失败: {endpoint}{item_id}/ - {status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ 清理测试数据异常: {str(e)}")
            return False
    
    def wait_for_condition(self, condition_func, timeout: int = 30, interval: float = 1.0) -> bool:
        """等待条件满足"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        return False
    
    def print_test_summary(self):
        """打印测试摘要"""
        total = self.test_results["passed"] + self.test_results["failed"]
        print(f"\n{'='*50}")
        print(f"测试摘要 - {self.test_name}")
        print(f"{'='*50}")
        print(f"总测试数: {total}")
        print(f"通过: {self.test_results['passed']}")
        print(f"失败: {self.test_results['failed']}")
        print(f"成功率: {(self.test_results['passed']/total*100):.1f}%" if total > 0 else "0%")
        
        if self.test_results["errors"]:
            print(f"\n错误详情:")
            for error in self.test_results["errors"]:
                print(f"  - {error}")
        
        print(f"{'='*50}")
    
    def run_test(self, test_func, *args, **kwargs):
        """运行单个测试"""
        try:
            self.logger.info(f"开始测试: {test_func.__name__}")
            result = test_func(*args, **kwargs)
            if result:
                self.test_results["passed"] += 1
            else:
                self.test_results["failed"] += 1
            return result
        except Exception as e:
            self.logger.error(f"测试异常: {str(e)}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_func.__name__}: {str(e)}")
            return False 
#!/usr/bin/env python3
"""
登录认证测试类
专门处理登录、登出、Token验证等认证相关测试
"""

import time
from test_base import BaseTester
from test_config import API_ENDPOINTS, TEST_ACCOUNTS

class AuthTester(BaseTester):
    """登录认证测试类"""
    
    def __init__(self):
        super().__init__("AuthTest")
    
    def test_admin_login_success(self) -> bool:
        """测试管理员登录成功"""
        self.logger.info("🔐 测试管理员登录成功...")
        
        # 清除之前的认证状态
        self.token = None
        self.session.headers.clear()
        
        # 使用管理员账号登录
        result = self.authenticate("admin")
        
        # 验证登录结果
        success = self.assert_status_code(
            200 if result else 401, 
            200, 
            "管理员登录"
        )
        
        if success:
            # 验证Token存在
            success = self.assert_response_contains(
                {"access": self.token} if self.token else {}, 
                "access", 
                "Token获取"
            )
        
        return success
    
    def test_admin_login_failure(self) -> bool:
        """测试管理员登录失败（错误密码）"""
        self.logger.info("🔐 测试管理员登录失败（错误密码）...")
        
        # 使用错误密码
        login_data = {
            "username": TEST_ACCOUNTS["admin"]["username"],
            "password": "wrong_password"
        }
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["auth"]["login"], login_data)
        
        return self.assert_status_code(status_code, 401, "管理员登录失败（错误密码）")
    
    def test_invalid_username_login(self) -> bool:
        """测试无效用户名登录"""
        self.logger.info("🔐 测试无效用户名登录...")
        
        login_data = {
            "username": "nonexistent_user",
            "password": "any_password"
        }
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["auth"]["login"], login_data)
        
        return self.assert_status_code(status_code, 401, "无效用户名登录")
    
    def test_empty_credentials_login(self) -> bool:
        """测试空凭据登录"""
        self.logger.info("🔐 测试空凭据登录...")
        
        # 测试空用户名
        login_data = {
            "username": "",
            "password": "any_password"
        }
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["auth"]["login"], login_data)
        success1 = self.assert_status_code(status_code, 400, "空用户名登录")
        
        # 测试空密码
        login_data = {
            "username": "admin",
            "password": ""
        }
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["auth"]["login"], login_data)
        success2 = self.assert_status_code(status_code, 400, "空密码登录")
        
        return success1 and success2
    
    def test_token_refresh(self) -> bool:
        """测试Token刷新"""
        self.logger.info("🔄 测试Token刷新...")
        
        # 先登录获取Token
        if not self.authenticate("admin"):
            self.logger.error("无法获取初始Token")
            return False
        
        # 获取refresh token
        login_data = {
            "username": TEST_ACCOUNTS["admin"]["username"],
            "password": TEST_ACCOUNTS["admin"]["password"]
        }
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["auth"]["login"], login_data)
        
        if status_code != 200:
            self.logger.error("无法获取refresh token")
            return False
        
        refresh_token = response.get("refresh")
        if not refresh_token:
            self.logger.error("响应中没有refresh token")
            return False
        
        # 使用refresh token获取新的access token
        refresh_data = {"refresh": refresh_token}
        status_code, response = self.make_request("POST", API_ENDPOINTS["auth"]["refresh"], refresh_data)
        
        success = self.assert_status_code(status_code, 200, "Token刷新")
        
        if success:
            # 验证新的access token
            new_access_token = response.get("access")
            success = self.assert_response_contains(response, "access", "新Token获取")
            
            if new_access_token:
                # 更新当前token
                self.token = new_access_token
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
        
        return success
    
    def test_token_validation(self) -> bool:
        """测试Token验证"""
        self.logger.info("🔍 测试Token验证...")
        
        # 先登录获取有效Token
        if not self.authenticate("admin"):
            self.logger.error("无法获取有效Token")
            return False
        
        # 使用有效Token访问受保护的API
        status_code, response = self.make_request("GET", API_ENDPOINTS["users"]["list"])
        success1 = self.assert_status_code(status_code, 200, "有效Token访问API")
        
        # 使用无效Token访问API
        invalid_token = "invalid_token_here"
        self.session.headers.update({"Authorization": f"Bearer {invalid_token}"})
        
        status_code, response = self.make_request("GET", API_ENDPOINTS["users"]["list"])
        success2 = self.assert_status_code(status_code, 401, "无效Token访问API")
        
        # 恢复有效Token
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        return success1 and success2
    
    def test_logout(self) -> bool:
        """测试登出功能"""
        self.logger.info("🚪 测试登出功能...")
        
        # 先登录
        if not self.authenticate("admin"):
            self.logger.error("无法登录进行登出测试")
            return False
        
        # 执行登出
        status_code, response = self.make_request("POST", API_ENDPOINTS["auth"]["logout"])
        
        # 验证登出成功
        success = self.assert_status_code(status_code, 200, "登出操作")
        
        if success:
            # 验证登出后无法访问受保护的API
            status_code, response = self.make_request("GET", API_ENDPOINTS["users"]["list"])
            success = self.assert_status_code(status_code, 401, "登出后访问API")
        
        return success
    
    def test_concurrent_login(self) -> bool:
        """测试并发登录"""
        self.logger.info("🔄 测试并发登录...")
        
        # 创建多个会话同时登录
        import threading
        import requests
        
        results = []
        
        def login_worker(worker_id):
            session = requests.Session()
            login_data = {
                "username": TEST_ACCOUNTS["admin"]["username"],
                "password": TEST_ACCOUNTS["admin"]["password"]
            }
            
            try:
                response = session.post(f"{self.base_url}{API_ENDPOINTS['auth']['login']}", json=login_data)
                results.append((worker_id, response.status_code == 200))
            except Exception as e:
                results.append((worker_id, False))
        
        # 启动多个线程同时登录
        threads = []
        for i in range(3):
            thread = threading.Thread(target=login_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有登录都成功
        all_success = all(success for _, success in results)
        success = self.assert_response_value(
            {"all_success": all_success}, 
            "all_success", 
            True, 
            "并发登录"
        )
        
        return success
    
    def run_all_tests(self):
        """运行所有认证测试"""
        self.logger.info("🚀 开始运行认证测试套件...")
        
        tests = [
            self.test_admin_login_success,
            self.test_admin_login_failure,
            self.test_invalid_username_login,
            self.test_empty_credentials_login,
            self.test_token_refresh,
            self.test_token_validation,
            self.test_logout,
            self.test_concurrent_login
        ]
        
        for test in tests:
            self.run_test(test)
        
        self.print_test_summary()
        return self.test_results["failed"] == 0

def main():
    """主函数"""
    print("🔐 CrewAI Platform 认证测试")
    print("=" * 50)
    
    tester = AuthTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 所有认证测试通过!")
    else:
        print("❌ 部分认证测试失败，请检查日志")
    
    return success

if __name__ == "__main__":
    main() 
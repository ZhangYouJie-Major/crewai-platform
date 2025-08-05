#!/usr/bin/env python3
"""
字典管理测试类
测试字典的创建、更新、删除、树结构、父子关系等功能
"""

import time
from test_base import BaseTester
from test_config import API_ENDPOINTS

class DictionaryManagementTester(BaseTester):
    """字典管理测试类"""
    
    def __init__(self):
        super().__init__("DictionaryManagementTest")
        self.created_dictionaries = []  # 记录创建的字典 ID，用于清理
    
    def test_create_dictionary(self) -> bool:
        """测试创建字典"""
        self.logger.info("➕ 测试创建字典...")
        
        # 创建测试数据
        dict_data = self.create_test_data("dictionary")
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], dict_data)
        
        success = self.assert_status_code(status_code, 201, "字典创建")
        
        if success:
            # 验证响应数据
            success = self.assert_response_contains(response, "id", "字典ID")
            success = self.assert_response_value(response, "name", dict_data["name"], "字典名称")
            
            # 记录创建的字典 ID用于清理
            if "id" in response:
                self.created_dictionaries.append(response["id"])
        
        return success
    
    def test_get_dictionary_list(self) -> bool:
        """测试获取字典列表"""
        self.logger.info("📋 测试获取字典列表...")
        
        status_code, response = self.make_request("GET", API_ENDPOINTS["dictionary"]["list"])
        
        success = self.assert_status_code(status_code, 200, "获取字典列表")
        
        if success:
            dictionaries = response.get("results", []) if isinstance(response, dict) else response
            self.logger.info(f"✅ 获取到 {len(dictionaries)} 个字典")
            
            # 验证列表结构
            if dictionaries:
                success = self.assert_response_contains(dictionaries[0], "id", "字典列表项ID")
                success = self.assert_response_contains(dictionaries[0], "name", "字典列表项名称")
                success = self.assert_response_contains(dictionaries[0], "description", "字典列表项描述")
        
        return success
    
    def test_get_dictionary_detail(self) -> bool:
        """测试获取字典详情"""
        self.logger.info("🔍 测试获取字典详情...")
        
        # 先获取字典列表
        status_code, response = self.make_request("GET", API_ENDPOINTS["dictionary"]["list"])
        
        if status_code != 200:
            self.logger.error("无法获取字典列表")
            return False
        
        dictionaries = response.get("results", []) if isinstance(response, dict) else response
        
        if not dictionaries:
            self.logger.warning("没有字典可测试详情")
            return True
        
        # 获取第一个字典的详情
        dict_id = dictionaries[0]["id"]
        status_code, response = self.make_request("GET", API_ENDPOINTS["dictionary"]["detail"].format(id=dict_id))
        
        success = self.assert_status_code(status_code, 200, "获取字典详情")
        
        if success:
            # 验证详情数据完整性
            required_fields = ["id", "name", "description", "parent"]
            for field in required_fields:
                success = self.assert_response_contains(response, field, f"字典详情字段: {field}")
        
        return success
    
    def test_update_dictionary(self) -> bool:
        """测试更新字典"""
        self.logger.info("✏️ 测试更新字典...")
        
        # 先获取字典列表
        status_code, response = self.make_request("GET", API_ENDPOINTS["dictionary"]["list"])
        
        if status_code != 200:
            self.logger.error("无法获取字典列表")
            return False
        
        dictionaries = response.get("results", []) if isinstance(response, dict) else response
        
        if not dictionaries:
            self.logger.warning("没有字典可测试更新")
            return True
        
        # 更新第一个字典
        dict_id = dictionaries[0]["id"]
        update_data = {
            "name": f"更新后的字典_{int(time.time())}",
            "description": "这是更新后的描述"
        }
        
        status_code, response = self.make_request("PATCH", API_ENDPOINTS["dictionary"]["update"].format(id=dict_id), update_data)
        
        success = self.assert_status_code(status_code, 200, "字典更新")
        
        if success:
            # 验证更新结果
            success = self.assert_response_value(response, "name", update_data["name"], "字典名称更新")
            success = self.assert_response_value(response, "description", update_data["description"], "字典描述更新")
        
        return success
    
    def test_create_dictionary_with_parent(self) -> bool:
        """测试创建带父级的字典"""
        self.logger.info("👨‍👩‍👧‍👦 测试创建带父级的字典...")
        
        # 先创建一个父字典
        parent_data = self.create_test_data("dictionary", name="父字典")
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], parent_data)
        
        if status_code != 201:
            self.logger.error("无法创建父字典")
            return False
        
        parent_id = response["id"]
        self.created_dictionaries.append(parent_id)
        
        # 创建子字典
        child_data = self.create_test_data("dictionary", name="子字典", parent=parent_id)
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], child_data)
        
        success = self.assert_status_code(status_code, 201, "子字典创建")
        
        if success:
            # 验证子字典的父级关系
            success = self.assert_response_value(response, "parent", parent_id, "子字典父级ID")
            
            # 记录子字典ID用于清理
            if "id" in response:
                self.created_dictionaries.append(response["id"])
        
        return success
    
    def test_get_dictionary_tree(self) -> bool:
        """测试获取字典树结构"""
        self.logger.info("🌳 测试获取字典树结构...")
        
        status_code, response = self.make_request("GET", API_ENDPOINTS["dictionary"]["tree"])
        
        success = self.assert_status_code(status_code, 200, "获取字典树")
        
        if success:
            # 验证树结构响应
            if isinstance(response, list):
                self.logger.info(f"✅ 获取到 {len(response)} 个根级字典")
                
                # 验证树结构字段
                if response:
                    root_dict = response[0]
                    success = self.assert_response_contains(root_dict, "id", "根字典ID")
                    success = self.assert_response_contains(root_dict, "name", "根字典名称")
                    success = self.assert_response_contains(root_dict, "children", "根字典子级")
            else:
                self.logger.warning("字典树响应格式不是列表")
        
        return success
    
    def test_dictionary_hierarchy(self) -> bool:
        """测试字典层级关系"""
        self.logger.info("🏗️ 测试字典层级关系...")
        
        # 创建三级字典结构：祖父 -> 父 -> 子
        grandfather_data = self.create_test_data("dictionary", name="祖父字典")
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], grandfather_data)
        
        if status_code != 201:
            self.logger.error("无法创建祖父字典")
            return False
        
        grandfather_id = response["id"]
        self.created_dictionaries.append(grandfather_id)
        
        # 创建父字典
        father_data = self.create_test_data("dictionary", name="父字典", parent=grandfather_id)
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], father_data)
        
        if status_code != 201:
            self.logger.error("无法创建父字典")
            return False
        
        father_id = response["id"]
        self.created_dictionaries.append(father_id)
        
        # 创建子字典
        child_data = self.create_test_data("dictionary", name="子字典", parent=father_id)
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], child_data)
        
        if status_code != 201:
            self.logger.error("无法创建子字典")
            return False
        
        child_id = response["id"]
        self.created_dictionaries.append(child_id)
        
        # 验证层级关系
        success = self.assert_response_value(response, "parent", father_id, "子字典父级")
        
        # 获取子字典详情，验证父级关系
        status_code, response = self.make_request("GET", API_ENDPOINTS["dictionary"]["detail"].format(id=child_id))
        
        if status_code == 200:
            success = self.assert_response_value(response, "parent", father_id, "子字典详情父级")
        
        return success
    
    def test_move_dictionary(self) -> bool:
        """测试移动字典位置"""
        self.logger.info("🔄 测试移动字典位置...")
        
        # 创建两个父字典
        parent1_data = self.create_test_data("dictionary", name="父字典1")
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], parent1_data)
        
        if status_code != 201:
            self.logger.error("无法创建父字典1")
            return False
        
        parent1_id = response["id"]
        self.created_dictionaries.append(parent1_id)
        
        parent2_data = self.create_test_data("dictionary", name="父字典2")
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], parent2_data)
        
        if status_code != 201:
            self.logger.error("无法创建父字典2")
            return False
        
        parent2_id = response["id"]
        self.created_dictionaries.append(parent2_id)
        
        # 创建子字典，初始属于父字典1
        child_data = self.create_test_data("dictionary", name="移动字典", parent=parent1_id)
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], child_data)
        
        if status_code != 201:
            self.logger.error("无法创建子字典")
            return False
        
        child_id = response["id"]
        self.created_dictionaries.append(child_id)
        
        # 验证初始父级
        success = self.assert_response_value(response, "parent", parent1_id, "初始父级")
        
        # 移动到父字典2
        move_data = {"parent": parent2_id}
        status_code, response = self.make_request("PATCH", API_ENDPOINTS["dictionary"]["update"].format(id=child_id), move_data)
        
        success = self.assert_status_code(status_code, 200, "字典移动")
        
        if success:
            # 验证移动后的父级
            success = self.assert_response_value(response, "parent", parent2_id, "移动后父级")
        
        return success
    
    def test_delete_dictionary_with_children(self) -> bool:
        """测试删除带子级的字典"""
        self.logger.info("🗑️ 测试删除带子级的字典...")
        
        # 创建父字典
        parent_data = self.create_test_data("dictionary", name="待删除父字典")
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], parent_data)
        
        if status_code != 201:
            self.logger.error("无法创建父字典")
            return False
        
        parent_id = response["id"]
        
        # 创建子字典
        child_data = self.create_test_data("dictionary", name="子字典", parent=parent_id)
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], child_data)
        
        if status_code != 201:
            self.logger.error("无法创建子字典")
            return False
        
        child_id = response["id"]
        
        # 尝试删除父字典（应该失败，因为有子级）
        status_code, response = self.make_request("DELETE", API_ENDPOINTS["dictionary"]["delete"].format(id=parent_id))
        
        # 应该返回400错误（有子级不能删除）
        success = self.assert_status_code(status_code, 400, "删除带子级的字典")
        
        # 先删除子字典
        status_code, response = self.make_request("DELETE", API_ENDPOINTS["dictionary"]["delete"].format(id=child_id))
        
        if status_code in [200, 204]:
            # 再删除父字典
            status_code, response = self.make_request("DELETE", API_ENDPOINTS["dictionary"]["delete"].format(id=parent_id))
            success = self.assert_status_code(status_code, 204, "删除父字典")
        else:
            self.logger.error("无法删除子字典")
            success = False
        
        return success
    
    def test_dictionary_validation(self) -> bool:
        """测试字典数据验证"""
        self.logger.info("✅ 测试字典数据验证...")
        
        # 测试缺少必需字段
        invalid_data = {
            "name": "",  # 空名称
            "description": "测试描述"
        }
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], invalid_data)
        
        success1 = self.assert_status_code(status_code, 400, "无效数据创建字典")
        
        # 测试无效的父级ID
        invalid_data = {
            "name": "测试字典",
            "description": "测试描述",
            "parent": 99999  # 不存在的父级ID
        }
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], invalid_data)
        
        success2 = self.assert_status_code(status_code, 400, "无效父级ID创建字典")
        
        return success1 and success2
    
    def test_dictionary_duplicate_name(self) -> bool:
        """测试字典名称重复"""
        self.logger.info("🔄 测试字典名称重复...")
        
        # 先创建一个字典
        dict_data = self.create_test_data("dictionary")
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], dict_data)
        
        if status_code != 201:
            self.logger.error("无法创建第一个字典")
            return False
        
        first_dict_id = response["id"]
        self.created_dictionaries.append(first_dict_id)
        
        # 尝试创建同名字典
        duplicate_data = {
            "name": dict_data["name"],  # 使用相同的名称
            "description": "重复名称字典"
        }
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["dictionary"]["create"], duplicate_data)
        
        # 应该返回400错误（名称重复）
        success = self.assert_status_code(status_code, 400, "重复名称字典创建")
        
        return success
    
    def cleanup_test_data(self):
        """清理测试数据"""
        self.logger.info("🧹 清理测试数据...")
        
        # 按层级顺序清理（先删除子级，再删除父级）
        for dict_id in reversed(self.created_dictionaries):
            try:
                status_code, response = self.make_request("DELETE", API_ENDPOINTS["dictionary"]["delete"].format(id=dict_id))
                if status_code in [200, 204]:
                    self.logger.info(f"✅ 清理字典 {dict_id} 成功")
                else:
                    self.logger.warning(f"⚠️ 清理字典 {dict_id} 失败: {status_code}")
            except Exception as e:
                self.logger.error(f"❌ 清理字典 {dict_id} 异常: {str(e)}")
        
        self.created_dictionaries.clear()
    
    def run_all_tests(self):
        """运行所有字典管理测试"""
        self.logger.info("🚀 开始运行字典管理测试套件...")
        
        # 先进行认证
        if not self.authenticate("admin"):
            self.logger.error("认证失败，无法运行测试")
            return False
        
        tests = [
            self.test_create_dictionary,
            self.test_get_dictionary_list,
            self.test_get_dictionary_detail,
            self.test_update_dictionary,
            self.test_create_dictionary_with_parent,
            self.test_get_dictionary_tree,
            self.test_dictionary_hierarchy,
            self.test_move_dictionary,
            self.test_delete_dictionary_with_children,
            self.test_dictionary_validation,
            self.test_dictionary_duplicate_name
        ]
        
        for test in tests:
            self.run_test(test)
        
        # 清理测试数据
        self.cleanup_test_data()
        
        self.print_test_summary()
        return self.test_results["failed"] == 0

def main():
    """主函数"""
    print("📚 CrewAI Platform 字典管理测试")
    print("=" * 50)
    
    tester = DictionaryManagementTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 所有字典管理测试通过!")
    else:
        print("❌ 部分字典管理测试失败，请检查日志")
    
    return success

if __name__ == "__main__":
    main() 
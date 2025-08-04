"""
字典管理功能测试

测试字典模型的CRUD操作、API接口、数据验证等功能
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from crewaiplatform.models import Dictionary

User = get_user_model()


class DictionaryModelTest(TestCase):
    """字典模型测试"""
    
    def setUp(self):
        """测试数据准备"""
        self.parent_dict = Dictionary.objects.create(
            code='llm_provider',
            name='LLM供应商',
            description='大语言模型供应商',
            sort_order=1,
            is_active=True
        )
        
        self.child_dict = Dictionary.objects.create(
            parent=self.parent_dict,
            code='openai',
            name='OpenAI',
            description='OpenAI公司',
            value='https://api.openai.com',
            sort_order=1,
            is_active=True
        )
    
    def test_dictionary_creation(self):
        """测试字典项创建"""
        self.assertEqual(self.parent_dict.code, 'llm_provider')
        self.assertEqual(self.parent_dict.name, 'LLM供应商')
        self.assertIsNone(self.parent_dict.parent)
        self.assertTrue(self.parent_dict.is_active)
    
    def test_dictionary_hierarchy(self):
        """测试字典层级关系"""
        self.assertEqual(self.child_dict.parent, self.parent_dict)
        self.assertIn(self.child_dict, self.parent_dict.children.all())
    
    def test_get_full_path(self):
        """测试获取完整路径"""
        self.assertEqual(self.parent_dict.get_full_path(), 'LLM供应商')
        self.assertEqual(self.child_dict.get_full_path(), 'LLM供应商 -> OpenAI')
    
    def test_get_level(self):
        """测试获取层级深度"""
        self.assertEqual(self.parent_dict.get_level(), 1)
        self.assertEqual(self.child_dict.get_level(), 2)
    
    def test_get_children(self):
        """测试获取子级字典项"""
        children = self.parent_dict.get_children()
        self.assertEqual(children.count(), 1)
        self.assertEqual(children.first(), self.child_dict)
    
    def test_str_representation(self):
        """测试字符串表示"""
        self.assertEqual(str(self.parent_dict), 'LLM供应商')
        self.assertEqual(str(self.child_dict), 'LLM供应商 -> OpenAI')


class DictionaryAPITest(APITestCase):
    """字典API测试"""
    
    def setUp(self):
        """测试数据准备"""
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 获取JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # 创建测试数据
        self.parent_dict = Dictionary.objects.create(
            code='test_parent',
            name='测试父级',
            description='测试父级字典项',
            sort_order=1,
            is_active=True
        )
        
        self.child_dict = Dictionary.objects.create(
            parent=self.parent_dict,
            code='test_child',
            name='测试子级',
            description='测试子级字典项',
            sort_order=1,
            is_active=True
        )
    
    def test_get_dictionary_list(self):
        """测试获取字典列表"""
        url = reverse('dictionary-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 父级和子级
    
    def test_get_dictionary_detail(self):
        """测试获取字典详情"""
        url = reverse('dictionary-detail', kwargs={'pk': self.parent_dict.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'test_parent')
        self.assertEqual(response.data['name'], '测试父级')
    
    def test_create_dictionary(self):
        """测试创建字典项"""
        url = reverse('dictionary-list')
        data = {
            'code': 'new_dict',
            'name': '新字典项',
            'description': '新创建的字典项',
            'sort_order': 2,
            'is_active': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'new_dict')
        self.assertEqual(response.data['name'], '新字典项')
        
        # 验证数据库中的记录
        new_dict = Dictionary.objects.get(code='new_dict')
        self.assertEqual(new_dict.name, '新字典项')
    
    def test_create_child_dictionary(self):
        """测试创建子级字典项"""
        url = reverse('dictionary-list')
        data = {
            'parent': self.parent_dict.id,
            'code': 'new_child',
            'name': '新子级项',
            'description': '新创建的子级字典项',
            'sort_order': 2,
            'is_active': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['parent'], self.parent_dict.id)
        self.assertEqual(response.data['code'], 'new_child')
    
    def test_update_dictionary(self):
        """测试更新字典项"""
        url = reverse('dictionary-detail', kwargs={'pk': self.parent_dict.id})
        data = {
            'code': 'test_parent',  # 代码不能修改
            'name': '更新后的名称',
            'description': '更新后的描述',
            'sort_order': 5,
            'is_active': False
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '更新后的名称')
        self.assertEqual(response.data['sort_order'], 5)
        self.assertFalse(response.data['is_active'])
        
        # 验证数据库中的更新
        updated_dict = Dictionary.objects.get(id=self.parent_dict.id)
        self.assertEqual(updated_dict.name, '更新后的名称')
        self.assertFalse(updated_dict.is_active)
    
    def test_delete_dictionary(self):
        """测试删除字典项"""
        url = reverse('dictionary-detail', kwargs={'pk': self.child_dict.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证数据库中的记录已删除
        self.assertFalse(Dictionary.objects.filter(id=self.child_dict.id).exists())
    
    def test_get_children_action(self):
        """测试获取子级字典项"""
        url = reverse('dictionary-children', kwargs={'pk': self.parent_dict.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], 'test_child')
    
    def test_get_tree_action(self):
        """测试获取树形结构"""
        url = reverse('dictionary-tree')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tree', response.data)
        
        # 检查树形结构
        tree = response.data['tree']
        self.assertTrue(len(tree) >= 1)
        
        # 找到测试的父级节点
        parent_node = next((node for node in tree if node['code'] == 'test_parent'), None)
        self.assertIsNotNone(parent_node)
        self.assertEqual(len(parent_node['children']), 1)
        self.assertEqual(parent_node['children'][0]['code'], 'test_child')
    
    def test_get_options_action(self):
        """测试获取字典选项"""
        url = reverse('dictionary-options')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        
        # 测试根级项目
        root_items = [item for item in response.data['items'] if not item.get('parent')]
        self.assertTrue(len(root_items) >= 1)
    
    def test_get_options_with_parent_code(self):
        """测试根据父级代码获取子级选项"""
        url = reverse('dictionary-options')
        response = self.client.get(url, {'parent_code': 'test_parent'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        
        # 应该只返回子级项目
        items = response.data['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['code'], 'test_child')
    
    def test_get_stats_action(self):
        """测试获取统计信息"""
        url = reverse('dictionary-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_items', response.data)
        self.assertIn('active_items', response.data)
        self.assertIn('root_items', response.data)
        self.assertIn('child_items', response.data)
        
        # 验证统计数据
        self.assertEqual(response.data['total_items'], 2)
        self.assertEqual(response.data['active_items'], 2)
        self.assertEqual(response.data['root_items'], 1)
        self.assertEqual(response.data['child_items'], 1)
    
    def test_batch_create_action(self):
        """测试批量创建字典项"""
        url = reverse('dictionary-batch-create')
        data = {
            'items': [
                {
                    'code': 'batch1',
                    'name': '批量项目1',
                    'description': '批量创建的项目1',
                    'sort_order': 1,
                    'is_active': True
                },
                {
                    'code': 'batch2',
                    'name': '批量项目2',
                    'description': '批量创建的项目2',
                    'sort_order': 2,
                    'is_active': True
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created_count'], 2)
        self.assertEqual(response.data['error_count'], 0)
        
        # 验证数据库中的记录
        self.assertTrue(Dictionary.objects.filter(code='batch1').exists())
        self.assertTrue(Dictionary.objects.filter(code='batch2').exists())
    
    def test_filter_by_parent_id(self):
        """测试根据父级ID筛选"""
        url = reverse('dictionary-list')
        response = self.client.get(url, {'parent_id': self.parent_dict.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], 'test_child')
    
    def test_filter_parent_only(self):
        """测试只获取父级项目"""
        url = reverse('dictionary-list')
        response = self.client.get(url, {'parent_only': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], 'test_parent')
    
    def test_filter_by_active_status(self):
        """测试根据激活状态筛选"""
        # 先将一个项目设为非激活状态
        self.child_dict.is_active = False
        self.child_dict.save()
        
        url = reverse('dictionary-list')
        response = self.client.get(url, {'is_active': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        active_items = [item for item in response.data if item['is_active']]
        self.assertEqual(len(active_items), 1)
        self.assertEqual(active_items[0]['code'], 'test_parent')
    
    def test_search_by_code_and_name(self):
        """测试根据代码和名称搜索"""
        url = reverse('dictionary-list')
        
        # 按代码搜索
        response = self.client.get(url, {'code': 'parent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        
        # 按名称搜索
        response = self.client.get(url, {'name': '测试'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 父级和子级都包含"测试"
    
    def test_unauthorized_access(self):
        """测试未认证访问"""
        # 清除认证信息
        self.client.credentials()
        
        url = reverse('dictionary-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_validation_errors(self):
        """测试数据验证错误"""
        url = reverse('dictionary-list')
        
        # 缺少必填字段
        data = {
            'description': '缺少代码和名称的项目'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 验证错误信息
        self.assertIn('code', response.data)
        self.assertIn('name', response.data)
    
    def test_circular_reference_prevention(self):
        """测试防止循环引用"""
        # 尝试将父级设置为子级的子级（这应该被阻止）
        url = reverse('dictionary-detail', kwargs={'pk': self.parent_dict.id})
        data = {
            'parent': self.child_dict.id,
            'code': 'test_parent',
            'name': '测试父级',
            'description': '尝试创建循环引用',
            'sort_order': 1,
            'is_active': True
        }
        response = self.client.put(url, data, format='json')
        
        # 应该返回验证错误
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DictionaryIntegrationTest(APITestCase):
    """字典功能集成测试"""
    
    def setUp(self):
        """测试数据准备"""
        self.user = User.objects.create_user(
            username='integrationuser',
            email='integration@example.com',
            password='testpass123'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_complete_dictionary_workflow(self):
        """测试完整的字典管理工作流"""
        # 1. 创建根级字典项
        create_url = reverse('dictionary-list')
        root_data = {
            'code': 'workflow_root',
            'name': '工作流根项',
            'description': '集成测试根项',
            'sort_order': 1,
            'is_active': True
        }
        response = self.client.post(create_url, root_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        root_id = response.data['id']
        
        # 2. 创建子级字典项
        child_data = {
            'parent': root_id,
            'code': 'workflow_child',
            'name': '工作流子项',
            'description': '集成测试子项',
            'sort_order': 1,
            'is_active': True
        }
        response = self.client.post(create_url, child_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        child_id = response.data['id']
        
        # 3. 获取列表验证创建结果
        list_url = reverse('dictionary-list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # 4. 获取树形结构
        tree_url = reverse('dictionary-tree')
        response = self.client.get(tree_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. 获取子级项目
        children_url = reverse('dictionary-children', kwargs={'pk': root_id})
        response = self.client.get(children_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # 6. 更新项目
        update_url = reverse('dictionary-detail', kwargs={'pk': child_id})
        update_data = {
            'parent': root_id,
            'code': 'workflow_child',
            'name': '更新后的子项',
            'description': '更新后的描述',
            'sort_order': 2,
            'is_active': True
        }
        response = self.client.put(update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '更新后的子项')
        
        # 7. 获取统计信息
        stats_url = reverse('dictionary-stats')
        response = self.client.get(stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_items'], 2)
        
        # 8. 删除子项
        delete_url = reverse('dictionary-detail', kwargs={'pk': child_id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 9. 验证删除结果
        response = self.client.get(list_url)
        self.assertEqual(len(response.data), 1)  # 只剩根项
        
        # 10. 删除根项
        delete_url = reverse('dictionary-detail', kwargs={'pk': root_id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 11. 验证所有项目都已删除
        response = self.client.get(list_url)
        self.assertEqual(len(response.data), 0)
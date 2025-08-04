<template>
  <div class="dictionary-management">
    <div class="header">
      <h2>字典管理</h2>
      <p class="description">管理系统字典配置，支持层级结构的字典项</p>
    </div>

    <el-card class="content-card">
      <!-- 操作栏 -->
      <div class="toolbar">
        <div class="left-actions">
          <el-button type="primary" @click="handleAddDictionary">
            <el-icon><Plus /></el-icon>
            新增字典项
          </el-button>
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button @click="handleViewTree">
            <el-icon><DataBoard /></el-icon>
            树形视图
          </el-button>
        </div>
        
        <div class="right-actions">
          <el-select
            v-model="filterParent"
            placeholder="筛选父级项目"
            clearable
            style="width: 200px; margin-right: 12px"
            @change="handleParentFilter"
          >
            <el-option
              v-for="item in parentOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
          
          <el-input
            v-model="searchKeyword"
            placeholder="搜索字典名称或代码"
            style="width: 250px"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </div>

      <!-- 字典项列表 -->
      <el-table 
        :data="dictionariesData" 
        v-loading="dictionariesLoading"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        row-key="id"
        :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#303133' }"
        :default-expand-all="false"
      >
        <el-table-column prop="name" label="名称" min-width="200">
          <template #default="scope">
            <div class="dictionary-name">
              <span class="name">{{ scope.row.name }}</span>
              <el-tag v-if="scope.row.children && scope.row.children.length > 0" size="small" type="info">
                {{ scope.row.children.length }} 项
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="code" label="代码" width="150">
          <template #default="scope">
            <el-text type="primary" class="code-text">{{ scope.row.code }}</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="full_path" label="完整路径" min-width="200">
          <template #default="scope">
            <el-text type="info" size="small">{{ scope.row.full_path }}</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="value" label="扩展值" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            <el-text v-if="scope.row.value" type="info" size="small">{{ scope.row.value }}</el-text>
            <el-text v-else type="info" size="small">-</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="sort_order" label="排序" width="80" align="center">
          <template #default="scope">
            <el-text type="info">{{ scope.row.sort_order }}</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="is_active" label="状态" width="80" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="scope">
            <el-text type="info" size="small">{{ formatDate(scope.row.created_at) }}</el-text>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEditDictionary(scope.row)" text>
              编辑
            </el-button>
            
            <el-button 
              type="primary" 
              size="small" 
              @click="handleAddChildDictionary(scope.row)"
              text
            >
              添加子项
            </el-button>
            
            <el-popconfirm
              title="确定要删除这个字典项吗？"
              @confirm="handleDeleteDictionary(scope.row)"
            >
              <template #reference>
                <el-button type="danger" size="small" text>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 字典项编辑对话框 -->
    <el-dialog
      v-model="dictionaryDialogVisible"
      :title="getDictionaryDialogTitle()"
      width="600px"
      destroy-on-close
    >
      <el-form 
        ref="dictionaryFormRef"
        :model="dictionaryForm" 
        :rules="dictionaryRules"
        label-width="120px"
      >
        <el-form-item 
          v-if="dictionaryForm.parent" 
          label="父级项目" 
          prop="parent"
        >
          <el-input 
            :value="parentItem?.name || `父级项目 (ID: ${dictionaryForm.parent})`" 
            disabled 
          />
          <div v-if="parentItem?.code" class="form-tip">
            父级代码: {{ parentItem.code }}
          </div>
          <div v-if="!parentItem?.name" class="form-tip" style="color: #f56c6c;">
            ⚠️ 无法获取父级项目详细信息，可能原因：
            <ul style="margin: 4px 0 0 16px; padding: 0;">
              <li>父级项目已被删除</li>
              <li>网络连接问题</li>
              <li>权限不足</li>
            </ul>
          </div>
        </el-form-item>
        
        <el-form-item label="字典代码" prop="code">
          <el-input 
            v-model="dictionaryForm.code" 
            placeholder="请输入字典代码，如：openai、gpt-4"
            :disabled="!!dictionaryForm.id"
          />
          <div class="form-tip">字典代码用于程序识别</div>
        </el-form-item>
        
        <el-form-item label="字典名称" prop="name">
          <el-input v-model="dictionaryForm.name" placeholder="请输入字典名称" />
        </el-form-item>
        
        <el-form-item label="扩展值" prop="value">
          <el-input 
            v-model="dictionaryForm.value" 
            type="textarea" 
            :rows="2"
            placeholder="请输入扩展值（可选）"
          />
          <div class="form-tip">可存储额外配置信息，如API端点等</div>
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="dictionaryForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入字典描述"
          />
        </el-form-item>
        
        <el-form-item label="排序顺序" prop="sort_order">
          <el-input-number v-model="dictionaryForm.sort_order" :min="0" :max="9999" />
          <div class="form-tip">数字越小排序越靠前</div>
        </el-form-item>
        
        <el-form-item label="是否启用" prop="is_active">
          <el-switch v-model="dictionaryForm.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dictionaryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveDictionary" :loading="saveLoading">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 树形视图对话框 -->
    <el-dialog
      v-model="treeDialogVisible"
      title="字典项树形视图"
      width="80%"
      destroy-on-close
    >
      <el-tree
        :data="treeData"
        :props="{ children: 'children', label: 'name' }"
        default-expand-all
        :expand-on-click-node="false"
        node-key="id"
        v-loading="treeLoading"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <span class="node-label">{{ data.name }}</span>
            <span class="node-code">({{ data.code }})</span>
            <el-tag v-if="!data.is_active" type="danger" size="small">禁用</el-tag>
          </div>
        </template>
      </el-tree>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search, DataBoard } from '@element-plus/icons-vue'
import api from '@/services/api'

// 响应式数据
const dictionariesData = ref([])
const dictionariesLoading = ref(false)
const searchKeyword = ref('')
const filterParent = ref(null)
const saveLoading = ref(false)
const treeData = ref([])
const treeLoading = ref(false)

// 对话框控制
const dictionaryDialogVisible = ref(false)
const treeDialogVisible = ref(false)

// 表单引用
const dictionaryFormRef = ref(null)

// 当前操作的父级项目
const parentItem = ref(null)

// 字典项表单
const dictionaryForm = reactive({
  id: null,
  parent: null,
  code: '',
  name: '',
  value: '',
  description: '',
  sort_order: 0,
  is_active: true
})

// 表单验证规则
const dictionaryRules = {
  code: [
    { required: true, message: '请输入字典代码', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入字典名称', trigger: 'blur' }
  ]
}

// 计算属性 - 父级选项
const parentOptions = computed(() => {
  const options = []
  const collectParents = (items) => {
    items.forEach(item => {
      if (!item.parent) {
        options.push({ id: item.id, name: item.name })
      }
      if (item.children && item.children.length > 0) {
        collectParents(item.children)
      }
    })
  }
  collectParents(dictionariesData.value)
  return options
})

// 方法定义
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

const getDictionaryDialogTitle = () => {
  if (dictionaryForm.id) {
    return '编辑字典项'
  } else if (dictionaryForm.parent) {
    return '新增子级字典项'
  } else {
    return '新增字典项'
  }
}

const resetDictionaryForm = () => {
  Object.assign(dictionaryForm, {
    id: null,
    parent: null,
    code: '',
    name: '',
    value: '',
    description: '',
    sort_order: 0,
    is_active: true
  })
}

// 处理树形数据，添加hasChildren属性
const processTreeData = (data) => {
  return data.map(item => {
    const processedItem = {
      ...item,
      hasChildren: item.children && item.children.length > 0
    }
    
    if (processedItem.children && processedItem.children.length > 0) {
      processedItem.children = processTreeData(processedItem.children)
    }
    
    return processedItem
  })
}

// 获取字典列表
const fetchDictionaries = async (params = {}) => {
  try {
    dictionariesLoading.value = true
    
    // 如果有特定的父级筛选或搜索条件，使用普通列表查询
    if (params.parent_id || params.name || params.code) {
      const response = await api.getDictionaries(params)
      let data = response.data.results || response.data || []
      // 为平铺数据添加hasChildren属性
      data = data.map(item => ({
        ...item,
        hasChildren: item.children_count > 0
      }))
      dictionariesData.value = data
    } else {
      // 否则获取树形结构数据
      const response = await api.getDictionaries({
        ...params,
        tree: true
      })
      let data = response.data.results || response.data || []
      // 为树形数据添加hasChildren属性
      dictionariesData.value = processTreeData(data)
    }
    
    console.log('获取到的字典数据:', dictionariesData.value)
  } catch (error) {
    console.error('获取字典列表失败:', error)
    ElMessage.error('获取字典列表失败')
  } finally {
    dictionariesLoading.value = false
  }
}

// 获取树形数据
const fetchTreeData = async () => {
  try {
    treeLoading.value = true
    const response = await api.getDictionaryTree()
    treeData.value = response.data.tree || []
  } catch (error) {
    console.error('获取树形数据失败:', error)
    ElMessage.error('获取树形数据失败')
  } finally {
    treeLoading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  const params = {}
  if (searchKeyword.value) {
    params.name = searchKeyword.value
    params.code = searchKeyword.value
  }
  if (filterParent.value) {
    params.parent_id = filterParent.value
  }
  fetchDictionaries(params)
}

// 父级筛选处理
const handleParentFilter = () => {
  handleSearch()
}

// 刷新数据
const refreshData = () => {
  handleSearch()
}

// 查看树形视图
const handleViewTree = async () => {
  treeDialogVisible.value = true
  await fetchTreeData()
}

// 字典项操作
const handleAddDictionary = () => {
  resetDictionaryForm()
  parentItem.value = null
  dictionaryDialogVisible.value = true
}

const handleAddChildDictionary = (parentRow) => {
  resetDictionaryForm()
  parentItem.value = parentRow
  dictionaryForm.parent = parentRow.id
  dictionaryDialogVisible.value = true
}

const handleEditDictionary = async (row) => {
  Object.assign(dictionaryForm, row)
  console.log('编辑字典项:', row)
  console.log('当前数据:', dictionariesData.value)
  
  if (row.parent) {
    console.log('查找父级项目 ID:', row.parent)
    
    // 首先检查当前行是否已经有父级信息（从展开的树形数据中）
    if (row.parent_name || row.parent_code) {
      console.log('从当前行数据中找到父级信息')
      parentItem.value = {
        id: row.parent,
        name: row.parent_name,
        code: row.parent_code
      }
    } else {
      // 首先尝试从树形结构中查找父级项目
      parentItem.value = findParentInTree(dictionariesData.value, row.parent)
      console.log('从树形结构中找到的父级项目:', parentItem.value)
      
      // 如果没找到，使用改进的查找函数尝试从当前数据中查找父级项目
      if (!parentItem.value) {
        parentItem.value = findParentById(dictionariesData.value, row.parent)
        console.log('从平铺数据中找到的父级项目:', parentItem.value)
      }
      
      // 如果还是没找到，尝试单独获取父级项目信息
      if (!parentItem.value) {
        try {
          console.log('尝试单独获取父级项目信息...')
          const parentResponse = await api.getDictionaryById(row.parent)
          parentItem.value = parentResponse.data
          console.log('单独获取的父级项目:', parentItem.value)
        } catch (error) {
          console.error('获取父级项目信息失败:', error)
          // 如果获取失败，显示错误信息并设置降级显示
          if (error.response?.status === 404) {
            console.warn('父级项目不存在，可能已被删除')
            parentItem.value = { 
              id: row.parent, 
              name: null,
              error: '父级项目不存在或已被删除'
            }
          } else if (error.response?.status === 403) {
            console.warn('没有权限访问父级项目')
            parentItem.value = { 
              id: row.parent, 
              name: null,
              error: '没有权限访问父级项目'
            }
          } else {
            console.warn('网络错误或其他问题')
            parentItem.value = { 
              id: row.parent, 
              name: null,
              error: '网络连接问题'
            }
          }
        }
      }
    }
  } else {
    parentItem.value = null
  }
  console.log('最终设置的父级项目:', parentItem.value)
  dictionaryDialogVisible.value = true
}

const findItemById = (items, id) => {
  for (const item of items) {
    if (item.id === id) {
      return item
    }
    if (item.children && item.children.length > 0) {
      const found = findItemById(item.children, id)
      if (found) return found
    }
  }
  return null
}

// 改进的父级项目查找函数，支持递归查找
const findParentById = (items, parentId) => {
  // 首先尝试在平铺的列表中查找
  const flattenItems = (items, result = []) => {
    items.forEach(item => {
      result.push(item)
      if (item.children && item.children.length > 0) {
        flattenItems(item.children, result)
      }
    })
    return result
  }
  
  const allItems = flattenItems(items)
  return allItems.find(item => item.id === parentId) || null
}

// 从树形结构中查找父级项目
const findParentInTree = (items, parentId) => {
  for (const item of items) {
    if (item.id === parentId) {
      return item
    }
    if (item.children && item.children.length > 0) {
      const found = findParentInTree(item.children, parentId)
      if (found) return found
    }
  }
  return null
}

const handleSaveDictionary = async () => {
  try {
    await dictionaryFormRef.value.validate()
    saveLoading.value = true
    
    if (dictionaryForm.id) {
      // 更新
      await api.updateDictionary(dictionaryForm.id, dictionaryForm)
      ElMessage.success('字典项更新成功')
    } else {
      // 创建
      await api.createDictionary(dictionaryForm)
      ElMessage.success('字典项创建成功')
    }
    
    dictionaryDialogVisible.value = false
    await handleSearch()
  } catch (error) {
    console.error('保存字典项失败:', error)
    ElMessage.error('保存字典项失败')
  } finally {
    saveLoading.value = false
  }
}

const handleDeleteDictionary = async (row) => {
  try {
    await api.deleteDictionary(row.id)
    ElMessage.success('字典项删除成功')
    await handleSearch()
  } catch (error) {
    console.error('删除字典项失败:', error)
    ElMessage.error('删除字典项失败')
  }
}

// 初始化
onMounted(() => {
  fetchDictionaries()
})
</script>

<style scoped>
.dictionary-management {
  padding: 20px;
}

.header {
  margin-bottom: 20px;
}

.header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.content-card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 0;
  border-bottom: 1px solid #ebeef5;
}

.left-actions {
  display: flex;
  gap: 12px;
}

.right-actions {
  display: flex;
  align-items: center;
}

.dictionary-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dictionary-name .name {
  font-weight: 500;
  flex: 1;
}

.code-text {
  font-family: 'Courier New', monospace;
  font-weight: 500;
}

.form-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.node-label {
  font-weight: 500;
}

.node-code {
  color: #909399;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .dictionary-management {
    color: #e4e7ed;
  }
}
</style>
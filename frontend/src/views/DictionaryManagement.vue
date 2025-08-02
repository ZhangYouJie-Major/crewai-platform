<template>
  <div class="dictionary-management">
    <div class="header">
      <h2>字典管理</h2>
      <p class="description">管理系统字典配置，支持两级字典结构</p>
    </div>

    <el-card class="content-card">
      <!-- 操作栏 -->
      <div class="toolbar">
        <div class="left-actions">
          <el-button type="primary" @click="handleAddDictionary">
            <el-icon><Plus /></el-icon>
            新增字典类型
          </el-button>
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
        
        <div class="right-actions">
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

      <!-- 字典类型列表 -->
      <el-table 
        :data="dictionariesData" 
        v-loading="dictionariesLoading"
        @expand-change="handleDictionaryExpand"
        row-key="id"
        :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#303133' }"
      >
        <el-table-column type="expand">
          <template #default="props">
            <div class="dictionary-items">
              <div class="items-header">
                <h4>{{ props.row.name }} - 字典项</h4>
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="handleAddItem(props.row)"
                >
                  <el-icon><Plus /></el-icon>
                  添加字典项
                </el-button>
              </div>
              
              <!-- 字典项树形表格 -->
              <el-table 
                :data="props.row.items || []"
                :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
                row-key="id"
                size="small"
                class="items-table"
                v-loading="itemsLoading"
                :header-cell-style="{ backgroundColor: '#f5f7fa !important', color: '#303133 !important' }"
              >
                <el-table-column prop="name" label="名称" min-width="150">
                  <template #default="scope">
                    <div class="item-name">
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
                
                <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
                
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
                
                <el-table-column label="操作" width="200" align="center">
                  <template #default="scope">
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="handleEditItem(scope.row)"
                      text
                    >
                      编辑
                    </el-button>
                    
                    <el-button 
                      v-if="!scope.row.parent"
                      type="primary" 
                      size="small" 
                      @click="handleAddChildItem(scope.row, props.row)"
                      text
                    >
                      添加子项
                    </el-button>
                    
                    <el-popconfirm
                      title="确定要删除这个字典项吗？"
                      @confirm="handleDeleteItem(scope.row)"
                    >
                      <template #reference>
                        <el-button type="danger" size="small" text>删除</el-button>
                      </template>
                    </el-popconfirm>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="字典名称" min-width="150">
          <template #default="scope">
            <div class="dictionary-name">
              <el-text size="large" class="name">{{ scope.row.name }}</el-text>
              <el-text type="info" size="small" class="code">({{ scope.row.code }})</el-text>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="item_count" label="字典项数量" width="120" align="center">
          <template #default="scope">
            <el-text type="primary">{{ scope.row.item_count || 0 }}</el-text>
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
        
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEditDictionary(scope.row)" text>
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除这个字典类型吗？"
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

    <!-- 字典类型编辑对话框 -->
    <el-dialog
      v-model="dictionaryDialogVisible"
      :title="dictionaryForm.id ? '编辑字典类型' : '新增字典类型'"
      width="600px"
      destroy-on-close
    >
      <el-form 
        ref="dictionaryFormRef"
        :model="dictionaryForm" 
        :rules="dictionaryRules"
        label-width="120px"
      >
        <el-form-item label="字典代码" prop="code">
          <el-input 
            v-model="dictionaryForm.code" 
            placeholder="请输入字典代码，如：llm_provider"
            :disabled="!!dictionaryForm.id"
          />
          <div class="form-tip">字典代码只能包含小写字母、数字和下划线，且必须以字母开头</div>
        </el-form-item>
        
        <el-form-item label="字典名称" prop="name">
          <el-input v-model="dictionaryForm.name" placeholder="请输入字典名称" />
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

    <!-- 字典项编辑对话框 -->
    <el-dialog
      v-model="itemDialogVisible"
      :title="getItemDialogTitle()"
      width="600px"
      destroy-on-close
    >
      <el-form 
        ref="itemFormRef"
        :model="itemForm" 
        :rules="itemRules"
        label-width="120px"
      >
        <el-form-item label="所属字典" prop="dictionary">
          <el-input :value="currentDictionary?.name" disabled />
        </el-form-item>
        
        <el-form-item 
          v-if="itemForm.parent" 
          label="父级项目" 
          prop="parent"
        >
          <el-input :value="parentItem?.name" disabled />
        </el-form-item>
        
        <el-form-item label="项目代码" prop="code">
          <el-input 
            v-model="itemForm.code" 
            placeholder="请输入项目代码"
            :disabled="!!itemForm.id"
          />
        </el-form-item>
        
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="itemForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        
        <el-form-item label="项目值" prop="value">
          <el-input 
            v-model="itemForm.value" 
            type="textarea" 
            :rows="2"
            placeholder="请输入项目值（可选）"
          />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="itemForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        
        <el-form-item label="排序顺序" prop="sort_order">
          <el-input-number v-model="itemForm.sort_order" :min="0" :max="9999" />
        </el-form-item>
        
        <el-form-item label="是否启用" prop="is_active">
          <el-switch v-model="itemForm.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="itemDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveItem" :loading="saveLoading">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import api from '@/services/api'

// 响应式数据
const dictionariesData = ref([])
const dictionariesLoading = ref(false)
const itemsLoading = ref(false)
const searchKeyword = ref('')
const saveLoading = ref(false)

// 对话框控制
const dictionaryDialogVisible = ref(false)
const itemDialogVisible = ref(false)

// 表单引用
const dictionaryFormRef = ref(null)
const itemFormRef = ref(null)

// 当前操作的字典和项目
const currentDictionary = ref(null)
const parentItem = ref(null)

// 字典类型表单
const dictionaryForm = reactive({
  id: null,
  code: '',
  name: '',
  description: '',
  sort_order: 0,
  is_active: true
})

// 字典项表单
const itemForm = reactive({
  id: null,
  dictionary: null,
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
    { required: true, message: '请输入字典代码', trigger: 'blur' },
    { pattern: /^[a-z][a-z0-9_]*$/, message: '字典代码只能包含小写字母、数字和下划线，且必须以字母开头', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入字典名称', trigger: 'blur' }
  ]
}

const itemRules = {
  code: [
    { required: true, message: '请输入项目代码', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' }
  ]
}

// 方法定义
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

const getItemDialogTitle = () => {
  if (itemForm.id) {
    return '编辑字典项'
  } else if (itemForm.parent) {
    return '新增子级字典项'
  } else {
    return '新增字典项'
  }
}

const resetDictionaryForm = () => {
  Object.assign(dictionaryForm, {
    id: null,
    code: '',
    name: '',
    description: '',
    sort_order: 0,
    is_active: true
  })
}

const resetItemForm = () => {
  Object.assign(itemForm, {
    id: null,
    dictionary: null,
    parent: null,
    code: '',
    name: '',
    value: '',
    description: '',
    sort_order: 0,
    is_active: true
  })
}

// 获取字典列表
const fetchDictionaries = async (search = '') => {
  try {
    dictionariesLoading.value = true
    const params = {}
    if (search) {
      params.name = search
      params.code = search
    }
    
    const response = await api.getDictionaries(params)
    dictionariesData.value = response.data.results || response.data || []
  } catch (error) {
    console.error('获取字典列表失败:', error)
    ElMessage.error('获取字典列表失败')
  } finally {
    dictionariesLoading.value = false
  }
}

// 获取字典项列表
const fetchDictionaryItems = async (dictionary) => {
  try {
    itemsLoading.value = true
    const response = await api.getDictionaryItems(dictionary.id, { tree_format: true })
    
    // 更新字典的items数据
    const dictIndex = dictionariesData.value.findIndex(d => d.id === dictionary.id)
    if (dictIndex !== -1) {
      dictionariesData.value[dictIndex].items = response.data
    }
  } catch (error) {
    console.error('获取字典项失败:', error)
    ElMessage.error('获取字典项失败')
  } finally {
    itemsLoading.value = false
  }
}

// 处理字典展开
const handleDictionaryExpand = async (row, expandedRows) => {
  if (expandedRows.find(item => item.id === row.id)) {
    // 展开时加载字典项
    await fetchDictionaryItems(row)
  }
}

// 搜索处理
const handleSearch = () => {
  fetchDictionaries(searchKeyword.value)
}

// 刷新数据
const refreshData = () => {
  fetchDictionaries(searchKeyword.value)
}

// 字典类型操作
const handleAddDictionary = () => {
  resetDictionaryForm()
  dictionaryDialogVisible.value = true
}

const handleEditDictionary = (row) => {
  Object.assign(dictionaryForm, row)
  dictionaryDialogVisible.value = true
}

const handleSaveDictionary = async () => {
  try {
    await dictionaryFormRef.value.validate()
    saveLoading.value = true
    
    if (dictionaryForm.id) {
      // 更新
      await api.updateDictionary(dictionaryForm.id, dictionaryForm)
      ElMessage.success('字典类型更新成功')
    } else {
      // 创建
      await api.createDictionary(dictionaryForm)
      ElMessage.success('字典类型创建成功')
    }
    
    dictionaryDialogVisible.value = false
    await fetchDictionaries(searchKeyword.value)
  } catch (error) {
    console.error('保存字典类型失败:', error)
    ElMessage.error('保存字典类型失败')
  } finally {
    saveLoading.value = false
  }
}

const handleDeleteDictionary = async (row) => {
  try {
    await api.deleteDictionary(row.id)
    ElMessage.success('字典类型删除成功')
    await fetchDictionaries(searchKeyword.value)
  } catch (error) {
    console.error('删除字典类型失败:', error)
    ElMessage.error('删除字典类型失败')
  }
}

// 字典项操作
const handleAddItem = (dictionary) => {
  resetItemForm()
  currentDictionary.value = dictionary
  parentItem.value = null
  itemForm.dictionary = dictionary.id
  itemForm.parent = null
  itemDialogVisible.value = true
}

const handleAddChildItem = (parentRow, dictionary) => {
  resetItemForm()
  currentDictionary.value = dictionary
  parentItem.value = parentRow
  itemForm.dictionary = dictionary.id
  itemForm.parent = parentRow.id
  itemDialogVisible.value = true
}

const handleEditItem = (row) => {
  Object.assign(itemForm, row)
  currentDictionary.value = dictionariesData.value.find(d => d.id === row.dictionary)
  if (row.parent) {
    // 找到父级项目
    parentItem.value = findItemById(currentDictionary.value.items, row.parent)
  } else {
    parentItem.value = null
  }
  itemDialogVisible.value = true
}

const findItemById = (items, id) => {
  for (const item of items) {
    if (item.id === id) {
      return item
    }
    if (item.children) {
      const found = findItemById(item.children, id)
      if (found) return found
    }
  }
  return null
}

const handleSaveItem = async () => {
  try {
    await itemFormRef.value.validate()
    saveLoading.value = true
    
    if (itemForm.id) {
      // 更新
      await api.updateDictionaryItem(itemForm.id, itemForm)
      ElMessage.success('字典项更新成功')
    } else {
      // 创建
      await api.createDictionaryItem(itemForm)
      ElMessage.success('字典项创建成功')
    }
    
    itemDialogVisible.value = false
    // 重新加载字典项
    await fetchDictionaryItems(currentDictionary.value)
  } catch (error) {
    console.error('保存字典项失败:', error)
    ElMessage.error('保存字典项失败')
  } finally {
    saveLoading.value = false
  }
}

const handleDeleteItem = async (row) => {
  try {
    await api.deleteDictionaryItem(row.id)
    ElMessage.success('字典项删除成功')
    // 重新加载字典项
    await fetchDictionaryItems(currentDictionary.value)
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

.dictionary-name {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dictionary-name .name {
  font-weight: 500;
}

.dictionary-name .code {
  font-family: 'Courier New', monospace;
}

.dictionary-items {
  padding: 16px;
  background-color: #f8f9fa;
  margin: 0 -20px;
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.items-header h4 {
  margin: 0;
  color: #303133;
}

.items-table {
  background-color: white;
  border-radius: 4px;
}

.items-table :deep(.el-table__header-wrapper) {
  background-color: #f5f7fa !important;
}

.items-table :deep(.el-table__header th) {
  background-color: #f5f7fa !important;
  color: #303133 !important;
  border-bottom: 1px solid #ebeef5;
}

.items-table :deep(.el-table__header .cell) {
  color: #303133 !important;
}

.item-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-name .name {
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

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .dictionary-items {
    background-color: #1a1a1a;
  }
  
  .items-table {
    background-color: #2d2d2d;
  }
}
</style>
<template>
  <el-dialog
    v-model="dialogVisible"
    title="聊天设置"
    width="500px"
    :before-close="handleClose"
  >
    <el-form :model="settingsForm" label-width="120px">
      <el-form-item label="主题设置">
        <el-radio-group v-model="settingsForm.theme">
          <el-radio label="light">浅色主题</el-radio>
          <el-radio label="dark">深色主题</el-radio>
          <el-radio label="auto">跟随系统</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="消息提醒">
        <el-switch 
          v-model="settingsForm.notifications" 
          active-text="开启" 
          inactive-text="关闭" 
        />
      </el-form-item>
      
      <el-form-item label="自动滚动">
        <el-switch 
          v-model="settingsForm.autoScroll" 
          active-text="开启" 
          inactive-text="关闭" 
        />
      </el-form-item>
      
      <el-form-item label="发送快捷键">
        <el-radio-group v-model="settingsForm.sendShortcut">
          <el-radio label="enter">Enter键发送</el-radio>
          <el-radio label="ctrl-enter">Ctrl+Enter发送</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'save'])

// 响应式数据
const dialogVisible = ref(false)
const settingsForm = ref({
  theme: 'light',
  notifications: true,
  autoScroll: true,
  sendShortcut: 'enter'
})

// 监听外部状态变化
watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  
  // 加载设置
  if (val) {
    loadSettings()
  }
})

// 监听内部状态变化
watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

// 方法
const loadSettings = () => {
  // 从localStorage加载设置
  const saved = localStorage.getItem('chat-settings')
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      Object.assign(settingsForm.value, parsed)
    } catch (error) {
      console.error('加载设置失败:', error)
    }
  }
}

const saveSettings = () => {
  try {
    // 保存到localStorage
    localStorage.setItem('chat-settings', JSON.stringify(settingsForm.value))
    
    // 触发保存事件
    emit('save', { ...settingsForm.value })
    
    // 关闭对话框
    dialogVisible.value = false
    
    ElMessage.success('设置已保存')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败')
  }
}

const handleClose = () => {
  dialogVisible.value = false
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
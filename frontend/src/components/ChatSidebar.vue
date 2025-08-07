<template>
  <div class="chat-sidebar">
    <!-- 搜索框 -->
    <div class="search-section">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索对话..."
        :prefix-icon="Search"
        size="small"
        clearable
      />
    </div>

    <!-- 对话列表 -->
    <div class="conversation-list" v-loading="loading">
      <div
        v-for="conversation in filteredConversations"
        :key="conversation.id"
        class="conversation-item"
        :class="{ active: conversation.id === currentConversationId }"
        @click="$emit('conversation-select', conversation.id)"
      >
        <div class="conversation-main">
          <div class="conversation-title">
            {{ conversation.title }}
          </div>
          <div class="conversation-preview">
            {{ getLastMessagePreview(conversation) }}
          </div>
          <div class="conversation-time">
            {{ formatTime(conversation.last_activity_at || conversation.created_at) }}
          </div>
        </div>
        
        <div class="conversation-actions">
          <el-dropdown trigger="click" @command="handleCommand">
            <el-button size="small" text :icon="More" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item 
                  :command="{ action: 'archive', id: conversation.id }"
                  :icon="Box"
                >
                  归档
                </el-dropdown-item>
                <el-dropdown-item 
                  :command="{ action: 'delete', id: conversation.id }"
                  :icon="Delete"
                  divided
                >
                  删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        
        <!-- 状态指示器 -->
        <div v-if="conversation.status !== 'active'" class="conversation-status">
          <el-tag size="small" type="info">
            {{ conversation.status === 'archived' ? '已归档' : conversation.status }}
          </el-tag>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="!loading && filteredConversations.length === 0" class="empty-state">
        <el-empty 
          :description="searchKeyword ? '未找到匹配的对话' : '暂无对话'"
          :image-size="80"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, More, Box, Delete } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  conversations: {
    type: Array,
    default: () => []
  },
  currentConversationId: {
    type: Number,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['conversation-select', 'conversation-delete', 'conversation-archive'])

// 响应式数据
const searchKeyword = ref('')

// 计算属性
const filteredConversations = computed(() => {
  if (!searchKeyword.value) {
    return props.conversations
  }
  
  return props.conversations.filter(conv => 
    conv.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    (conv.latest_message?.content && 
     conv.latest_message.content.toLowerCase().includes(searchKeyword.value.toLowerCase()))
  )
})

// 方法
const getLastMessagePreview = (conversation) => {
  if (conversation.latest_message) {
    const content = conversation.latest_message.content
    return content.length > 50 ? content.substring(0, 50) + '...' : content
  }
  return '暂无消息'
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  const oneDay = 24 * 60 * 60 * 1000
  const oneWeek = 7 * oneDay
  
  if (diff < oneDay) {
    // 今天 - 显示时间
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  } else if (diff < oneWeek) {
    // 一周内 - 显示星期
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return weekdays[date.getDay()]
  } else {
    // 超过一周 - 显示日期
    return date.toLocaleDateString('zh-CN', { 
      month: '2-digit', 
      day: '2-digit' 
    })
  }
}

const handleCommand = (command) => {
  const { action, id } = command
  
  switch (action) {
    case 'archive':
      emit('conversation-archive', id)
      break
    case 'delete':
      emit('conversation-delete', id)
      break
  }
}
</script>

<style scoped>
.chat-sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.search-section {
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  position: relative;
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.conversation-item:hover {
  background-color: #f8f9fa;
}

.conversation-item.active {
  background-color: #e6f7ff;
  border-left: 3px solid #1890ff;
}

.conversation-main {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-preview {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-time {
  font-size: 11px;
  color: #c0c4cc;
}

.conversation-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.conversation-item:hover .conversation-actions {
  opacity: 1;
}

.conversation-status {
  position: absolute;
  top: 8px;
  right: 8px;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
}
</style>
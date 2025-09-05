<template>
  <div class="chat-management">
    <div class="management-header">
      <h3>聊天管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="chats"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column prop="message" label="消息内容" min-width="300" show-overflow-tooltip />
      <el-table-column prop="room" label="聊天室" width="120" />
      <el-table-column prop="created_at" label="发送时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleView(row)">查看</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const loading = ref(false)
const chats = ref<any[]>([])

const loadChats = async () => {
  loading.value = true
  try {
    // 模拟数据
    chats.value = [
      {
        id: 1,
        user: { username: 'user1' },
        message: '大家好！',
        room: '公共聊天室',
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载聊天数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (chat: any) => {
  console.log('查看聊天:', chat)
}

const handleDelete = (chat: any) => {
  console.log('删除聊天:', chat)
}

onMounted(() => {
  loadChats()
})
</script>

<style scoped>
.chat-management {
  padding: 0;
}

.management-header {
  margin-bottom: 20px;
}

.management-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}
</style>

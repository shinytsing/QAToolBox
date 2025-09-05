<template>
  <div class="ai-writing-management">
    <div class="management-header">
      <h3>AI文案管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="aiWritings"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column prop="prompt" label="提示词" min-width="200" show-overflow-tooltip />
      <el-table-column prop="content" label="生成内容" min-width="300" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="180" />
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
const aiWritings = ref<any[]>([])

const loadAIWritings = async () => {
  loading.value = true
  try {
    // 模拟数据
    aiWritings.value = [
      {
        id: 1,
        user: { username: 'user1' },
        prompt: '写一首关于春天的诗',
        content: '春风拂面花满园，绿柳成荫鸟语喧...',
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载AI文案数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (aiWriting: any) => {
  console.log('查看AI文案:', aiWriting)
}

const handleDelete = (aiWriting: any) => {
  console.log('删除AI文案:', aiWriting)
}

onMounted(() => {
  loadAIWritings()
})
</script>

<style scoped>
.ai-writing-management {
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

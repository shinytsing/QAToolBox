<template>
  <div class="story-management">
    <div class="management-header">
      <h3>故事生成管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="stories"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column prop="prompt" label="提示词" min-width="200" show-overflow-tooltip />
      <el-table-column prop="title" label="故事标题" min-width="200" />
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
const stories = ref<any[]>([])

const loadStories = async () => {
  loading.value = true
  try {
    // 模拟数据
    stories.value = [
      {
        id: 1,
        user: { username: 'user1' },
        prompt: '写一个关于魔法世界的故事',
        title: '魔法世界的冒险',
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载故事生成数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (story: any) => {
  console.log('查看故事:', story)
}

const handleDelete = (story: any) => {
  console.log('删除故事:', story)
}

onMounted(() => {
  loadStories()
})
</script>

<style scoped>
.story-management {
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

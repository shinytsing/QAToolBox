<template>
  <div class="tarot-management">
    <div class="management-header">
      <h3>塔罗占卜管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="tarots"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column prop="question" label="问题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="card_name" label="抽到的牌" width="120" />
      <el-table-column prop="created_at" label="占卜时间" width="180" />
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
const tarots = ref<any[]>([])

const loadTarots = async () => {
  loading.value = true
  try {
    // 模拟数据
    tarots.value = [
      {
        id: 1,
        user: { username: 'user1' },
        question: '我的爱情运势如何？',
        card_name: '恋人',
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载塔罗占卜数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (tarot: any) => {
  console.log('查看塔罗占卜:', tarot)
}

const handleDelete = (tarot: any) => {
  console.log('删除塔罗占卜:', tarot)
}

onMounted(() => {
  loadTarots()
})
</script>

<style scoped>
.tarot-management {
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

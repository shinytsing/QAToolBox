<template>
  <div class="analysis-management">
    <div class="management-header">
      <h3>数据分析管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="analyses"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column prop="data_type" label="数据类型" width="120" />
      <el-table-column prop="analysis_type" label="分析类型" width="120" />
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
const analyses = ref<any[]>([])

const loadAnalyses = async () => {
  loading.value = true
  try {
    // 模拟数据
    analyses.value = [
      {
        id: 1,
        user: { username: 'user1' },
        data_type: 'CSV',
        analysis_type: '统计分析',
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载数据分析失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (analysis: any) => {
  console.log('查看数据分析:', analysis)
}

const handleDelete = (analysis: any) => {
  console.log('删除数据分析:', analysis)
}

onMounted(() => {
  loadAnalyses()
})
</script>

<style scoped>
.analysis-management {
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

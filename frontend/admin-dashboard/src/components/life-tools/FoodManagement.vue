<template>
  <div class="food-management">
    <div class="management-header">
      <h3>食物推荐管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="foods"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="食物名称" width="200" />
      <el-table-column prop="category" label="分类" width="120" />
      <el-table-column prop="calories" label="卡路里" width="100" />
      <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const loading = ref(false)
const foods = ref<any[]>([])

const loadFoods = async () => {
  loading.value = true
  try {
    // 模拟数据
    foods.value = [
      {
        id: 1,
        name: '苹果',
        category: '水果',
        calories: 52,
        description: '富含维生素C和膳食纤维',
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载食物数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleEdit = (food: any) => {
  console.log('编辑食物:', food)
}

const handleDelete = (food: any) => {
  console.log('删除食物:', food)
}

onMounted(() => {
  loadFoods()
})
</script>

<style scoped>
.food-management {
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

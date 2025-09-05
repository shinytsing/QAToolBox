<template>
  <div class="share-widgets-management">
    <div class="management-header">
      <h3>分享组件管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="shareWidgets"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-column prop="widget_type" label="组件类型" width="120" />
      <el-table-column prop="usage_count" label="使用次数" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusTag(row.status)">
            {{ getStatusName(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
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
const shareWidgets = ref<any[]>([])

const getStatusTag = (status: string) => {
  const tags: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    deprecated: 'warning'
  }
  return tags[status] || 'default'
}

const getStatusName = (status: string) => {
  const names: Record<string, string> = {
    active: '活跃',
    inactive: '非活跃',
    deprecated: '已废弃'
  }
  return names[status] || '未知'
}

const loadShareWidgets = async () => {
  loading.value = true
  try {
    // 模拟数据
    shareWidgets.value = [
      {
        id: 1,
        user: { username: 'user1' },
        widget_type: '分享按钮',
        usage_count: 42,
        status: 'active',
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载分享组件数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (widget: any) => {
  console.log('查看分享组件:', widget)
}

const handleDelete = (widget: any) => {
  console.log('删除分享组件:', widget)
}

onMounted(() => {
  loadShareWidgets()
})
</script>

<style scoped>
.share-widgets-management {
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

<template>
  <div class="pwa-management">
    <div class="management-header">
      <h3>PWA管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="pwaInstalls"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column prop="device_type" label="设备类型" width="120" />
      <el-table-column prop="browser" label="浏览器" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusTag(row.status)">
            {{ getStatusName(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="安装时间" width="180" />
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
const pwaInstalls = ref<any[]>([])

const getStatusTag = (status: string) => {
  const tags: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    uninstalled: 'danger'
  }
  return tags[status] || 'default'
}

const getStatusName = (status: string) => {
  const names: Record<string, string> = {
    active: '活跃',
    inactive: '非活跃',
    uninstalled: '已卸载'
  }
  return names[status] || '未知'
}

const loadPWAInstalls = async () => {
  loading.value = true
  try {
    // 模拟数据
    pwaInstalls.value = [
      {
        id: 1,
        user: { username: 'user1' },
        device_type: 'Mobile',
        browser: 'Chrome',
        status: 'active',
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载PWA安装数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (pwa: any) => {
  console.log('查看PWA安装:', pwa)
}

const handleDelete = (pwa: any) => {
  console.log('删除PWA安装:', pwa)
}

onMounted(() => {
  loadPWAInstalls()
})
</script>

<style scoped>
.pwa-management {
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

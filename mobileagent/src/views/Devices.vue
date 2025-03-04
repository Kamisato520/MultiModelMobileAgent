<template>
  <div class="devices-container">
    <!-- 顶部操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" @click="refreshDevices">
        <el-icon><Refresh /></el-icon>刷新设备
      </el-button>
      <el-input
        v-model="searchQuery"
        placeholder="搜索设备"
        style="width: 200px; margin-left: 16px"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 设备列表 -->
    <el-table
      v-loading="deviceStore.loading"
      :data="filteredDevices"
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column prop="id" label="设备ID" width="180" />
      <el-table-column prop="name" label="设备名称" width="180" />
      <el-table-column prop="model" label="型号" width="150" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="最后连接时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.lastConnected) }}
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button
            :type="row.status === 'connected' ? 'danger' : 'primary'"
            size="small"
            @click="handleConnectionToggle(row)"
          >
            {{ row.status === 'connected' ? '断开连接' : '连接设备' }}
          </el-button>
          <el-button
            type="primary"
            size="small"
            plain
            @click="showDeviceDetail(row)"
          >
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 设备详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="设备详情"
      width="600px"
    >
      <template v-if="selectedDevice">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="设备ID">
            {{ selectedDevice.id }}
          </el-descriptions-item>
          <el-descriptions-item label="设备名称">
            {{ selectedDevice.name }}
          </el-descriptions-item>
          <el-descriptions-item label="型号">
            {{ selectedDevice.model }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedDevice.status)">
              {{ selectedDevice.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="系统版本">
            {{ selectedDevice.systemVersion }}
          </el-descriptions-item>
          <el-descriptions-item label="最后连接时间">
            {{ formatDate(selectedDevice.lastConnected) }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 设备任务历史 -->
        <div class="task-history" style="margin-top: 20px">
          <h3>最近任务</h3>
          <el-table :data="deviceTasks" style="width: 100%">
            <el-table-column prop="id" label="任务ID" width="100" />
            <el-table-column prop="name" label="任务名称" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getTaskStatusType(row.status)">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createTime" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.createTime) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDeviceStore } from '@/store/device'
import { useTaskStore } from '@/store/task'
import { Refresh, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Store
const deviceStore = useDeviceStore()
const taskStore = useTaskStore()

// 状态
const searchQuery = ref('')
const detailDialogVisible = ref(false)
const selectedDevice = ref(null)
const deviceTasks = ref([])

// 计算属性
const filteredDevices = computed(() => {
  if (!searchQuery.value) return deviceStore.devices
  const query = searchQuery.value.toLowerCase()
  return deviceStore.devices.filter(device => 
    device.name.toLowerCase().includes(query) ||
    device.id.toLowerCase().includes(query)
  )
})

// 方法
const refreshDevices = async () => {
  try {
    await deviceStore.fetchDevices()
    ElMessage.success('设备列表已更新')
  } catch (error) {
    ElMessage.error('更新设备列表失败')
  }
}

const handleConnectionToggle = async (device) => {
  try {
    if (device.status === 'connected') {
      await deviceStore.disconnectDevice(device.id)
      ElMessage.success('设备已断开连接')
    } else {
      await deviceStore.connectDevice(device.id)
      ElMessage.success('设备已连接')
    }
  } catch (error) {
    ElMessage.error('操作失败：' + error.message)
  }
}

const showDeviceDetail = async (device) => {
  selectedDevice.value = device
  detailDialogVisible.value = true
  // 获取设备相关的任务
  deviceTasks.value = await taskStore.fetchTasksByDevice(device.id)
}

const getStatusType = (status) => {
  const types = {
    'connected': 'success',
    'disconnected': 'info',
    'error': 'danger'
  }
  return types[status] || 'info'
}

const getTaskStatusType = (status) => {
  const types = {
    'running': 'primary',
    'completed': 'success',
    'failed': 'danger',
    'pending': 'info'
  }
  return types[status] || 'info'
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString()
}

// 生命周期
onMounted(async () => {
  await refreshDevices()
})
</script>

<style scoped lang="scss">
.devices-container {
  padding: 20px;

  .operation-bar {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
  }

  .task-history {
    h3 {
      margin-bottom: 16px;
      color: #606266;
    }
  }
}
</style> 
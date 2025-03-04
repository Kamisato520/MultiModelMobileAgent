<template>
  <div class="monitor-container">
    <!-- 状态概览卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="status-card">
          <template #header>
            <div class="card-header">
              <span>设备总数</span>
            </div>
          </template>
          <div class="card-content">
            <span class="number">{{ deviceStore.devices.length }}</span>
            <span class="label">台</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="status-card">
          <template #header>
            <div class="card-header">
              <span>在线设备</span>
            </div>
          </template>
          <div class="card-content">
            <span class="number">{{ deviceStore.connectedDevices.length }}</span>
            <span class="label">台</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="status-card">
          <template #header>
            <div class="card-header">
              <span>运行中任务</span>
            </div>
          </template>
          <div class="card-content">
            <span class="number">{{ taskStore.runningTasks.length }}</span>
            <span class="label">个</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="status-card">
          <template #header>
            <div class="card-header">
              <span>任务完成率</span>
            </div>
          </template>
          <div class="card-content">
            <span class="number">{{ completionRate }}</span>
            <span class="label">%</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时监控面板 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>实时任务执行</span>
              <el-switch
                v-model="autoRefresh"
                active-text="自动刷新"
                @change="handleAutoRefreshChange"
              />
            </div>
          </template>
          <div class="task-monitor">
            <el-table
              :data="taskStore.runningTasks"
              style="width: 100%"
              v-loading="loading"
            >
              <el-table-column prop="id" label="任务ID" width="120" />
              <el-table-column prop="name" label="任务名称" width="180" />
              <el-table-column prop="deviceName" label="执行设备" width="150" />
              <el-table-column label="执行进度" width="200">
                <template #default="{ row }">
                  <el-progress
                    :percentage="row.progress || 0"
                    :status="getProgressStatus(row.status)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button
                    type="danger"
                    size="small"
                    @click="handleStopTask(row)"
                  >
                    停止
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="device-status">
          <template #header>
            <div class="card-header">
              <span>设备状态</span>
            </div>
          </template>
          <div class="device-list">
            <div
              v-for="device in deviceStore.devices"
              :key="device.id"
              class="device-item"
            >
              <div class="device-info">
                <el-avatar
                  :size="32"
                  :class="device.status"
                  icon="Monitor"
                />
                <div class="device-details">
                  <span class="device-name">{{ device.name }}</span>
                  <span class="device-status">
                    <el-tag
                      :type="getStatusType(device.status)"
                      size="small"
                    >
                      {{ device.status }}
                    </el-tag>
                  </span>
                </div>
              </div>
              <div class="device-tasks" v-if="device.status === 'connected'">
                <small>当前任务：{{ getDeviceCurrentTask(device.id) || '无' }}</small>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统日志 -->
    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>系统日志</span>
              <el-button
                type="primary"
                size="small"
                plain
                @click="clearLogs"
              >
                清空日志
              </el-button>
            </div>
          </template>
          <div class="log-container" ref="logContainer">
            <div
              v-for="(log, index) in systemLogs"
              :key="index"
              :class="['log-item', log.level]"
            >
              <span class="log-time">{{ formatTime(log.time) }}</span>
              <span class="log-level">
                <el-tag
                  :type="getLogType(log.level)"
                  size="small"
                >
                  {{ log.level }}
                </el-tag>
              </span>
              <span class="log-content">{{ log.message }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDeviceStore } from '@/store/device'
import { useTaskStore } from '@/store/task'
import { useWebSocketStore } from '@/store/websocket'
import { ElMessage } from 'element-plus'

// Store
const deviceStore = useDeviceStore()
const taskStore = useTaskStore()
const wsStore = useWebSocketStore()

// 状态
const loading = ref(false)
const autoRefresh = ref(true)
const refreshInterval = ref(null)
const systemLogs = ref([])
const logContainer = ref(null)

// 计算属性
const completionRate = computed(() => {
  const total = taskStore.tasks.length
  if (!total) return 0
  const completed = taskStore.tasks.filter(t => t.status === 'completed').length
  return Math.round((completed / total) * 100)
})

// 方法
const handleAutoRefreshChange = (value) => {
  if (value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  refreshInterval.value = setInterval(async () => {
    await refreshData()
  }, 5000) // 每5秒刷新一次
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      deviceStore.fetchDevices(),
      taskStore.fetchTasks()
    ])
  } catch (error) {
    ElMessage.error('刷新数据失败')
  } finally {
    loading.value = false
  }
}

const handleStopTask = async (task) => {
  try {
    await taskStore.stopTask(task.id)
    ElMessage.success('任务已停止')
  } catch (error) {
    ElMessage.error('停止任务失败')
  }
}

const getDeviceCurrentTask = (deviceId) => {
  const task = taskStore.runningTasks.find(t => t.deviceId === deviceId)
  return task ? task.name : null
}

const getStatusType = (status) => {
  const types = {
    'connected': 'success',
    'disconnected': 'info',
    'error': 'danger',
    'running': 'primary',
    'completed': 'success',
    'failed': 'danger'
  }
  return types[status] || 'info'
}

const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return ''
}

const getLogType = (level) => {
  const types = {
    'info': '',
    'warning': 'warning',
    'error': 'danger'
  }
  return types[level] || ''
}

const formatTime = (time) => {
  return new Date(time).toLocaleTimeString()
}

const addLog = (level, message) => {
  systemLogs.value.push({
    time: new Date(),
    level,
    message
  })
  // 保持最新的100条日志
  if (systemLogs.value.length > 100) {
    systemLogs.value.shift()
  }
  // 滚动到最新日志
  setTimeout(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}

const clearLogs = () => {
  systemLogs.value = []
}

// WebSocket 消息处理
const handleWebSocketMessage = (message) => {
  const { type, data } = message
  switch (type) {
    case 'device_status':
      addLog('info', `设备 ${data.deviceName} 状态更新为 ${data.status}`)
      break
    case 'task_update':
      addLog('info', `任务 ${data.taskName} 进度更新: ${data.progress}%`)
      break
    case 'error':
      addLog('error', data.message)
      break
  }
}

// 生命周期
onMounted(() => {
  refreshData()
  if (autoRefresh.value) {
    startAutoRefresh()
  }
  // 订阅 WebSocket 消息
  wsStore.socket?.addEventListener('message', handleWebSocketMessage)
})

onUnmounted(() => {
  stopAutoRefresh()
  // 取消订阅 WebSocket 消息
  wsStore.socket?.removeEventListener('message', handleWebSocketMessage)
})
</script>

<style scoped lang="scss">
.monitor-container {
  padding: 20px;

  .status-card {
    .card-content {
      text-align: center;
      
      .number {
        font-size: 36px;
        font-weight: bold;
        color: #409eff;
      }

      .label {
        margin-left: 8px;
        color: #909399;
      }
    }
  }

  .device-status {
    .device-list {
      max-height: 400px;
      overflow-y: auto;

      .device-item {
        padding: 12px;
        border-bottom: 1px solid #ebeef5;

        &:last-child {
          border-bottom: none;
        }

        .device-info {
          display: flex;
          align-items: center;
          gap: 12px;

          .device-details {
            flex: 1;

            .device-name {
              display: block;
              font-weight: 500;
            }

            .device-status {
              margin-top: 4px;
            }
          }
        }

        .device-tasks {
          margin-top: 8px;
          color: #909399;
        }
      }
    }
  }

  .log-container {
    height: 300px;
    overflow-y: auto;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 4px;

    .log-item {
      margin-bottom: 8px;
      font-family: monospace;

      .log-time {
        color: #909399;
        margin-right: 8px;
      }

      .log-level {
        margin-right: 8px;
      }

      &.error .log-content {
        color: #f56c6c;
      }

      &.warning .log-content {
        color: #e6a23c;
      }
    }
  }
}
</style> 
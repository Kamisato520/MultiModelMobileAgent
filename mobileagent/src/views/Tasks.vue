<template>
  <div class="tasks-container">
    <!-- 顶部操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" @click="showCreateTaskDialog">
        <el-icon><Plus /></el-icon>新建任务
      </el-button>
      <el-button @click="refreshTasks">
        <el-icon><Refresh /></el-icon>刷新
      </el-button>
      <div class="filters">
        <el-select
          v-model="statusFilter"
          placeholder="任务状态"
          clearable
          style="width: 120px; margin-right: 16px"
        >
          <el-option
            v-for="status in taskStatuses"
            :key="status.value"
            :label="status.label"
            :value="status.value"
          />
        </el-select>
        <el-input
          v-model="searchQuery"
          placeholder="搜索任务"
          style="width: 200px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 任务列表 -->
    <el-table
      v-loading="taskStore.loading"
      :data="paginatedTasks"
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column prop="id" label="任务ID" width="120" />
      <el-table-column prop="name" label="任务名称" width="180" />
      <el-table-column prop="deviceName" label="目标设备" width="150" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.createTime) }}
        </template>
      </el-table-column>
      <el-table-column prop="progress" label="进度" width="180">
        <template #default="{ row }">
          <el-progress
            :percentage="row.progress || 0"
            :status="getProgressStatus(row.status)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button-group>
            <el-popconfirm
              v-if="row.status === 'running'"
              title="确定要停止该任务吗？"
              @confirm="handleTaskAction(row, 'stop')"
            >
              <template #reference>
                <el-button type="danger" size="small">
                  <el-icon><VideoPause /></el-icon>停止
                </el-button>
              </template>
            </el-popconfirm>
            <el-button
              v-if="row.status === 'pending'"
              type="primary"
              size="small"
              @click="handleTaskAction(row, 'start')"
            >
              <el-icon><VideoPlay /></el-icon>启动
            </el-button>
            <el-button
              type="primary"
              size="small"
              plain
              @click="showTaskDetail(row)"
            >
              <el-icon><Document /></el-icon>详情
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="filteredTasks.length"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      class="pagination"
    />

    <!-- 创建任务对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建新任务"
      width="600px"
    >
      <el-form
        ref="taskFormRef"
        :model="taskForm"
        :rules="taskRules"
        label-width="100px"
      >
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" />
        </el-form-item>
        <el-form-item label="目标设备" prop="deviceId">
          <el-select v-model="taskForm.deviceId" style="width: 100%">
            <el-option
              v-for="device in deviceStore.connectedDevices"
              :key="device.id"
              :label="device.name"
              :value="device.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="指令输入" prop="instruction">
          <el-tabs v-model="inputMode">
            <el-tab-pane label="文本" name="text">
              <el-input
                v-model="taskForm.instruction"
                type="textarea"
                rows="4"
                placeholder="请输入自动化指令..."
              />
            </el-tab-pane>
            <el-tab-pane label="语音" name="voice">
              <div class="voice-input">
                <el-button
                  :type="isRecording ? 'danger' : 'primary'"
                  @click="toggleRecording"
                >
                  <el-icon>
                    <Microphone v-if="!isRecording" />
                    <VideoPause v-else />
                  </el-icon>
                  {{ isRecording ? '停止录音' : '开始录音' }}
                </el-button>
                <span v-if="isRecording" class="recording-tip">
                  正在录音...{{ recordingTime }}s
                </span>
              </div>
            </el-tab-pane>
            <el-tab-pane label="图像" name="image">
              <el-upload
                class="image-uploader"
                :action="uploadUrl"
                :show-file-list="false"
                :on-success="handleImageSuccess"
                :before-upload="beforeImageUpload"
              >
                <img
                  v-if="taskForm.imageUrl"
                  :src="taskForm.imageUrl"
                  class="uploaded-image"
                />
                <el-icon v-else class="image-uploader-icon"><Plus /></el-icon>
              </el-upload>
            </el-tab-pane>
          </el-tabs>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createTask" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="任务详情"
      width="800px"
    >
      <el-descriptions
        v-if="selectedTask"
        :column="2"
        border
      >
        <el-descriptions-item label="任务ID">
          {{ selectedTask.id }}
        </el-descriptions-item>
        <el-descriptions-item label="任务名称">
          {{ selectedTask.name }}
        </el-descriptions-item>
        <el-descriptions-item label="目标设备">
          {{ selectedTask.deviceName }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(selectedTask.status)">
            {{ selectedTask.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(selectedTask.createTime) }}
        </el-descriptions-item>
        <el-descriptions-item label="完成时间" v-if="selectedTask.completeTime">
          {{ formatDate(selectedTask.completeTime) }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 任务日志 -->
      <div v-if="selectedTask" class="task-logs">
        <h3>执行日志</h3>
        <el-timeline>
          <el-timeline-item
            v-for="log in selectedTask.logs"
            :key="log.id"
            :timestamp="formatDate(log.timestamp)"
            :type="getLogType(log.level)"
          >
            {{ log.message }}
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTaskStore } from '@/store/task'
import { useDeviceStore } from '@/store/device'
import {
  Plus, Refresh, Search, Document, VideoPlay, VideoPause,
  Microphone
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Store
const taskStore = useTaskStore()
const deviceStore = useDeviceStore()

// 状态
const searchQuery = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const createDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const selectedTask = ref(null)
const inputMode = ref('text')
const isRecording = ref(false)
const recordingTime = ref(0)
const recordingTimer = ref(null)
const creating = ref(false)

// 表单
const taskFormRef = ref(null)
const taskForm = ref({
  name: '',
  deviceId: '',
  instruction: '',
  imageUrl: ''
})

// 表单规则
const taskRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  deviceId: [{ required: true, message: '请选择目标设备', trigger: 'change' }],
  instruction: [{ required: true, message: '请输入指令', trigger: 'blur' }]
}

// 任务状态选项
const taskStatuses = [
  { label: '等待中', value: 'pending' },
  { label: '执行中', value: 'running' },
  { label: '已完成', value: 'completed' },
  { label: '已失败', value: 'failed' }
]

// 计算属性
const filteredTasks = computed(() => {
  let tasks = taskStore.tasks
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    tasks = tasks.filter(task => 
      task.name.toLowerCase().includes(query) ||
      task.id.toLowerCase().includes(query)
    )
  }
  
  if (statusFilter.value) {
    tasks = tasks.filter(task => task.status === statusFilter.value)
  }
  
  return tasks
})

const paginatedTasks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredTasks.value.slice(start, end)
})

// 方法
const refreshTasks = async () => {
  try {
    await taskStore.fetchTasks()
    ElMessage.success('任务列表已更新')
  } catch (error) {
    ElMessage.error('更新任务列表失败')
  }
}

const showCreateTaskDialog = () => {
  taskForm.value = {
    name: '',
    deviceId: '',
    instruction: '',
    imageUrl: ''
  }
  createDialogVisible.value = true
}

const createTask = async () => {
  if (!taskFormRef.value) return
  
  try {
    await taskFormRef.value.validate()
    creating.value = true
    
    await taskStore.createTask({
      ...taskForm.value,
      inputMode: inputMode.value
    })
    
    ElMessage.success('任务创建成功')
    createDialogVisible.value = false
  } catch (error) {
    ElMessage.error('任务创建失败：' + error.message)
  } finally {
    creating.value = false
  }
}

const handleTaskAction = async (task, action) => {
  try {
    await taskStore[`${action}Task`](task.id)
    ElMessage.success(`任务${action === 'start' ? '启动' : '停止'}成功`)
  } catch (error) {
    ElMessage.error(`操作失败：${error.message}`)
  }
}

const showTaskDetail = async (task) => {
  selectedTask.value = task
  detailDialogVisible.value = true
  // 获取任务详细信息（包括日志）
  await taskStore.fetchTaskDetail(task.id)
}

const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = () => {
  isRecording.value = true
  recordingTime.value = 0
  recordingTimer.value = setInterval(() => {
    recordingTime.value++
  }, 1000)
  // TODO: 实现录音逻辑
}

const stopRecording = () => {
  isRecording.value = false
  clearInterval(recordingTimer.value)
  // TODO: 实现停止录音和语音识别逻辑
}

const beforeImageUpload = (file) => {
  // 图片上传前的验证逻辑
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB！')
  }

  return isImage && isLt2M
}

const handleImageSuccess = (response) => {
  taskForm.value.imageUrl = response.url
  taskForm.value.instruction = response.recognizedText // 如果有OCR结果
}

// 辅助方法
const getStatusType = (status) => {
  const types = {
    'pending': 'info',
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
    'info': 'primary',
    'warning': 'warning',
    'error': 'danger'
  }
  return types[level] || 'info'
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString()
}

// 生命周期
onMounted(async () => {
  await refreshTasks()
  await deviceStore.fetchDevices() // 获取设备列表用于任务创建
})
</script>

<style scoped lang="scss">
.tasks-container {
  padding: 20px;

  .operation-bar {
    display: flex;
    align-items: center;
    margin-bottom: 20px;

    .filters {
      margin-left: auto;
      display: flex;
      align-items: center;
    }
  }

  .pagination {
    margin-top: 20px;
    justify-content: flex-end;
  }

  .voice-input {
    display: flex;
    align-items: center;
    gap: 16px;

    .recording-tip {
      color: #f56c6c;
    }
  }

  .image-uploader {
    :deep(.el-upload) {
      border: 1px dashed #d9d9d9;
      border-radius: 6px;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      transition: border-color 0.3s;

      &:hover {
        border-color: #409eff;
      }
    }

    .image-uploader-icon {
      font-size: 28px;
      color: #8c939d;
      width: 178px;
      height: 178px;
      text-align: center;
      line-height: 178px;
    }

    .uploaded-image {
      width: 178px;
      height: 178px;
      display: block;
    }
  }

  .task-logs {
    margin-top: 20px;
    
    h3 {
      margin-bottom: 16px;
      color: #606266;
    }
  }
}
</style> 
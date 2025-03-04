<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    :width="width"
    :close-on-click-modal="false"
  >
    <div class="confirm-content">
      <el-icon v-if="type === 'warning'" class="warning-icon">
        <Warning />
      </el-icon>
      <el-icon v-else-if="type === 'error'" class="error-icon">
        <CircleClose />
      </el-icon>
      <span class="message">{{ message }}</span>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleCancel">{{ cancelText }}</el-button>
        <el-button
          :type="confirmButtonType"
          @click="handleConfirm"
          :loading="loading"
        >
          {{ confirmText }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { Warning, CircleClose } from '@element-plus/icons-vue'
import { ref } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: '确认'
  },
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'warning',
    validator: (value) => ['warning', 'error', 'info'].includes(value)
  },
  width: {
    type: String,
    default: '420px'
  },
  confirmText: {
    type: String,
    default: '确认'
  },
  cancelText: {
    type: String,
    default: '取消'
  },
  confirmButtonType: {
    type: String,
    default: 'primary'
  }
})

const emit = defineEmits(['confirm', 'cancel'])

const dialogVisible = ref(false)
const loading = ref(false)

const handleConfirm = async () => {
  loading.value = true
  try {
    await emit('confirm')
  } finally {
    loading.value = false
    dialogVisible.value = false
  }
}

const handleCancel = () => {
  emit('cancel')
  dialogVisible.value = false
}

// 对外暴露打开对话框的方法
defineExpose({
  show: () => {
    dialogVisible.value = true
  }
})
</script>

<style scoped lang="scss">
.confirm-content {
  display: flex;
  align-items: center;
  padding: 20px 0;

  .warning-icon {
    font-size: 24px;
    color: #e6a23c;
    margin-right: 12px;
  }

  .error-icon {
    font-size: 24px;
    color: #f56c6c;
    margin-right: 12px;
  }

  .message {
    font-size: 14px;
    color: #606266;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 
<template>
  <el-tag
    :type="type"
    :effect="effect"
    :size="size"
  >
    <el-icon v-if="showIcon" class="status-icon">
      <component :is="icon" />
    </el-icon>
    <slot>{{ label }}</slot>
  </el-tag>
</template>

<script setup>
import {
  Success,
  Warning,
  CircleClose,
  Loading,
  InfoFilled
} from '@element-plus/icons-vue'
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  size: {
    type: String,
    default: 'default'
  },
  effect: {
    type: String,
    default: 'light'
  },
  showIcon: {
    type: Boolean,
    default: true
  }
})

const statusMap = {
  success: {
    type: 'success',
    icon: Success,
    label: '成功'
  },
  warning: {
    type: 'warning',
    icon: Warning,
    label: '警告'
  },
  error: {
    type: 'danger',
    icon: CircleClose,
    label: '错误'
  },
  loading: {
    type: 'info',
    icon: Loading,
    label: '加载中'
  },
  info: {
    type: 'info',
    icon: InfoFilled,
    label: '信息'
  }
}

const type = computed(() => statusMap[props.status]?.type || 'info')
const icon = computed(() => statusMap[props.status]?.icon || InfoFilled)
const label = computed(() => statusMap[props.status]?.label || props.status)
</script>

<style scoped lang="scss">
.status-icon {
  margin-right: 4px;
  vertical-align: middle;
}
</style> 
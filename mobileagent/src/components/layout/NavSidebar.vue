<template>
  <el-menu
    class="nav-sidebar"
    :default-active="currentRoute"
    :router="true"
  >
    <el-menu-item index="/devices">
      <el-icon><Monitor /></el-icon>
      <span>设备管理</span>
    </el-menu-item>
    <el-menu-item index="/tasks">
      <el-icon><List /></el-icon>
      <span>任务管理</span>
    </el-menu-item>
    <el-menu-item index="/monitor">
      <el-icon><VideoPlay /></el-icon>
      <span>实时监控</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Monitor, List, VideoPlay } from '@element-plus/icons-vue'

const route = useRoute()
const currentRoute = computed(() => route.path)
</script>

<style scoped lang="scss">
.nav-sidebar {
  height: 100%;
  border-right: solid 1px #e6e6e6;
}
</style> 
<template>
  <div class="nav-header">
    <div class="logo">
      <img src="@/assets/logo.png" alt="Mobile Agent" />
      <span>Mobile Agent</span>
    </div>
    <el-menu
      mode="horizontal"
      :router="true"
      :default-active="currentRoute"
    >
      <el-menu-item index="/">首页</el-menu-item>
      <el-menu-item index="/devices">设备管理</el-menu-item>
      <el-menu-item index="/tasks">任务管理</el-menu-item>
      <el-menu-item index="/monitor">实时监控</el-menu-item>
    </el-menu>
    <div class="user-info">
      <el-dropdown>
        <span class="el-dropdown-link">
          管理员 <el-icon><arrow-down /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>个人设置</el-dropdown-item>
            <el-dropdown-item divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'

const route = useRoute()
const currentRoute = computed(() => route.path)
</script>

<style scoped lang="scss">
.nav-header {
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);

  .logo {
    display: flex;
    align-items: center;
    margin-right: 40px;

    img {
      width: 32px;
      height: 32px;
      margin-right: 8px;
    }

    span {
      font-size: 18px;
      font-weight: 600;
      color: #001529;
    }
  }

  .user-info {
    margin-left: auto;
    cursor: pointer;
  }
}
</style> 
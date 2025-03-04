<template>
  <el-container class="app-container">
    <el-header height="60px">
      <nav-header />
    </el-header>
    
    <el-container>
      <el-aside width="200px">
        <nav-sidebar />
      </el-aside>
      
      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import NavHeader from '@/components/layout/NavHeader.vue'
import NavSidebar from '@/components/layout/NavSidebar.vue'
</script>

<style lang="scss">
.app-container {
  height: 100vh;
  
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.3s ease;
  }

  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }
}
</style>

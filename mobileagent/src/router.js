import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/devices',
    name: 'Devices',
    component: () => import('@/views/Devices.vue'),
    meta: { title: '设备管理' }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/Tasks.vue'),
    meta: { title: '任务管理' }
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: () => import('@/views/Monitor.vue'),
    meta: { title: '实时监控' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面未找到' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局导航守卫
router.beforeEach((to, from, next) => {
  // 更新页面标题
  document.title = `${to.meta.title} - Mobile Agent`
  next()
})

export default router 
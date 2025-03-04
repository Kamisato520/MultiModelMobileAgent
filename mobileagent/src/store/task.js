import { defineStore } from 'pinia'
import axios from 'axios'

export const useTaskStore = defineStore('task', {
  state: () => ({
    tasks: [],
    loading: false,
    error: null,
    currentTask: null
  }),

  getters: {
    runningTasks: (state) => state.tasks.filter(t => t.status === 'running'),
    tasksByDevice: (state) => (deviceId) => 
      state.tasks.filter(t => t.deviceId === deviceId)
  },

  actions: {
    async fetchTasks() {
      this.loading = true
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/tasks`)
        this.tasks = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async createTask(taskData) {
      try {
        const response = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL}/tasks`,
          taskData
        )
        this.tasks.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      }
    },

    updateTaskStatus(taskId, status) {
      const task = this.tasks.find(t => t.id === taskId)
      if (task) {
        task.status = status
      }
    }
  }
}) 
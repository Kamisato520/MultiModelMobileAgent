import { defineStore } from 'pinia'
import { useDeviceStore } from './device'
import { useTaskStore } from './task'

export const useWebSocketStore = defineStore('websocket', {
  state: () => ({
    socket: null,
    connected: false,
    reconnectAttempts: 0,
    maxReconnectAttempts: 5
  }),

  actions: {
    initializeWebSocket() {
      const wsUrl = import.meta.env.VITE_WS_URL
      this.socket = new WebSocket(wsUrl)
      
      this.socket.onopen = this.handleConnect
      this.socket.onclose = this.handleDisconnect
      this.socket.onmessage = this.handleMessage
      this.socket.onerror = this.handleError
    },

    handleConnect() {
      this.connected = true
      this.reconnectAttempts = 0
      console.log('WebSocket connected')
    },

    handleDisconnect() {
      this.connected = false
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++
          this.initializeWebSocket()
        }, import.meta.env.VITE_WS_RECONNECT_INTERVAL)
      }
    },

    handleMessage(event) {
      const data = JSON.parse(event.data)
      const deviceStore = useDeviceStore()
      const taskStore = useTaskStore()

      switch (data.type) {
        case 'device_status':
          deviceStore.updateDeviceStatus(data.deviceId, data.status)
          break
        case 'task_update':
          taskStore.updateTaskStatus(data.taskId, data.status)
          break
        // 处理其他消息类型
      }
    },

    handleError(error) {
      console.error('WebSocket error:', error)
    },

    sendMessage(message) {
      if (this.connected && this.socket) {
        this.socket.send(JSON.stringify(message))
      }
    }
  }
}) 
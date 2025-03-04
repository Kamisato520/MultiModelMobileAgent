import { defineStore } from 'pinia'
import axios from 'axios'

export const useDeviceStore = defineStore('device', {
  state: () => ({
    devices: [],
    loading: false,
    error: null,
    selectedDevice: null
  }),

  getters: {
    connectedDevices: (state) => state.devices.filter(d => d.status === 'connected'),
    deviceById: (state) => (id) => state.devices.find(d => d.id === id)
  },

  actions: {
    async fetchDevices() {
      this.loading = true
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/devices`)
        this.devices = response.data
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    updateDeviceStatus(deviceId, status) {
      const device = this.devices.find(d => d.id === deviceId)
      if (device) {
        device.status = status
      }
    },

    setSelectedDevice(device) {
      this.selectedDevice = device
    }
  }
}) 
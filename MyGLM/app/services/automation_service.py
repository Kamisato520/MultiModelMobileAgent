# backend/app/services/automation_service.py
from airtest.core.api import *
from airtest.core.android import Android
import logging

class AutomationService:
    def __init__(self):
        self.devices = {}
        self.logger = logging.getLogger(__name__)

    async def connect_device(self, device_id):
        """连接设备"""
        try:
            if device_id not in self.devices:
                device = Android(device_id)
                self.devices[device_id] = device
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect device {device_id}: {str(e)}")
            return False

    async def execute_action(self, device_id, action):
        """执行自动化操作"""
        try:
            device = self.devices.get(device_id)
            if not device:
                raise Exception("Device not connected")

            action_type = action['type']
            params = action['params']

            if action_type == 'touch':
                touch(Template(params['image']))
            elif action_type == 'swipe':
                swipe(params['start_pos'], params['end_pos'])
            elif action_type == 'text':
                text(params['content'])
            elif action_type == 'wait':
                wait(Template(params['image']))
            elif action_type == 'snapshot':
                snapshot(filename=params.get('filename', 'screen.png'))
            elif action_type == 'keyevent':
                keyevent(params['key'])
            elif action_type == 'sleep':
                sleep(params['duration'])

            return True
        except Exception as e:
            self.logger.error(f"Action execution failed: {str(e)}")
            return False

    async def disconnect_device(self, device_id):
        """断开设备连接"""
        try:
            if device_id in self.devices:
                device = self.devices[device_id]
                device.disconnect()
                del self.devices[device_id]
            return True
        except Exception as e:
            self.logger.error(f"Failed to disconnect device {device_id}: {str(e)}")
            return False

    def get_device_info(self, device_id):
        """获取设备信息"""
        try:
            device = self.devices.get(device_id)
            if device:
                return {
                    'connected': True,
                    'resolution': device.get_current_resolution(),
                    'orientation': device.get_current_orientation(),
                    'package': device.get_top_activity_name()
                }
            return {'connected': False}
        except Exception as e:
            self.logger.error(f"Failed to get device info: {str(e)}")
            return {'connected': False, 'error': str(e)}

# 确保导出 AutomationService 类
__all__ = ['AutomationService']
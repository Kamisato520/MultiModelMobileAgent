from enum import Enum
from datetime import datetime
from app import db
from dataclasses import dataclass
from typing import Dict, Optional

class DeviceType(Enum):
    """设备类型"""
    ANDROID = "android"
    IOS = "ios"
    UNKNOWN = "unknown"

class DeviceStatus(Enum):
    """设备状态"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"

@dataclass
class DeviceCapability:
    """设备能力描述"""
    supports_touch: bool = True
    supports_input: bool = True
    supports_gestures: bool = True
    supports_screenshot: bool = True
    min_android_version: Optional[str] = None
    max_android_version: Optional[str] = None
    required_permissions: list[str] = None

    def to_dict(self) -> Dict:
        return {
            "supports_touch": self.supports_touch,
            "supports_input": self.supports_input,
            "supports_gestures": self.supports_gestures,
            "supports_screenshot": self.supports_screenshot,
            "min_android_version": self.min_android_version,
            "max_android_version": self.max_android_version,
            "required_permissions": self.required_permissions or []
        }

class Device(db.Model):
    """设备模型"""
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(64))
    type = db.Column(db.Enum(DeviceType), default=DeviceType.UNKNOWN)
    status = db.Column(db.Enum(DeviceStatus), default=DeviceStatus.OFFLINE)
    platform_version = db.Column(db.String(32))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    capabilities = db.Column(db.JSON, default=DeviceCapability().to_dict)

    def __init__(self, device_id: str, name: str = None, device_type: DeviceType = DeviceType.UNKNOWN):
        self.device_id = device_id
        self.name = name or device_id
        self.type = device_type
        self.update_capabilities()

    def update_capabilities(self):
        """更新设备能力"""
        if self.type == DeviceType.ANDROID:
            self.capabilities = DeviceCapability(
                supports_touch=True,
                supports_input=True,
                supports_gestures=True,
                supports_screenshot=True,
                min_android_version="5.0",
                required_permissions=[
                    "android.permission.WRITE_EXTERNAL_STORAGE",
                    "android.permission.READ_EXTERNAL_STORAGE"
                ]
            ).to_dict()
        elif self.type == DeviceType.IOS:
            # iOS设备暂不支持自动化
            self.capabilities = DeviceCapability(
                supports_touch=False,
                supports_input=False,
                supports_gestures=False,
                supports_screenshot=False
            ).to_dict()

    def is_automation_supported(self) -> bool:
        """检查设备是否支持自动化"""
        return (
            self.type == DeviceType.ANDROID and
            self.status == DeviceStatus.ONLINE and
            self.capabilities.get('supports_touch', False)
        )

    def get_automation_constraints(self) -> Dict:
        """获取自动化约束条件"""
        if not self.is_automation_supported():
            return {
                "supported": False,
                "reason": "Device does not support automation" if self.type != DeviceType.ANDROID
                         else "Device is offline" if self.status != DeviceStatus.ONLINE
                         else "Device lacks required capabilities"
            }
        
        return {
            "supported": True,
            "platform": "Android",
            "version": self.platform_version,
            "capabilities": self.capabilities
        }

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'type': self.type.value,
            'status': self.status.value,
            'platform_version': self.platform_version,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'capabilities': self.capabilities,
            'automation_supported': self.is_automation_supported()
        }

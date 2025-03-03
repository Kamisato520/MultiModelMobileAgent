# backend/app/services/automation_service.py
import uiautomator2 as u2
from app.utils.logger import logger
from app.utils.exceptions import DeviceError, AutomationError
from enum import Enum
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from functools import wraps
import asyncio
import base64
from io import BytesIO
from PIL import Image
from app.services.llm_service import LLMService
from app.utils.cache import cache_llm_response

# 重试装饰器
def retry_on_error(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Action failed (attempt {attempt + 1}/{max_retries}): {str(e)}"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
            raise last_error
        return wrapper
    return decorator

class ActionType(Enum):
    """扩展的自动化动作类型"""
    # 基础操作
    CLICK = "click"
    LONG_CLICK = "long_click"
    DOUBLE_CLICK = "double_click"
    INPUT = "input"
    CLEAR = "clear"
    
    # 手势操作
    SWIPE = "swipe"
    PINCH = "pinch"
    ZOOM = "zoom"
    
    # 系统操作
    LAUNCH_APP = "launch_app"
    CLOSE_APP = "close_app"
    BACK = "back"
    HOME = "home"
    
    # 等待和断言
    WAIT = "wait"
    WAIT_GONE = "wait_gone"
    ASSERT = "assert"
    
    # 组合动作
    SEQUENCE = "sequence"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"

@dataclass
class ActionParam:
    """动作参数定义"""
    name: str
    type: type
    required: bool = True
    description: str = ""
    default: Optional[Union[str, int, float, bool, list, dict]] = None
    validator: Optional[callable] = None

# 扩展的动作定义
AVAILABLE_ACTIONS = {
    ActionType.CLICK: {
        "description": "点击指定元素",
        "params": {
            "target": ActionParam(
                name="target",
                type=str,
                description="目标元素文本/ID/坐标"
            ),
            "timeout": ActionParam(
                name="timeout",
                type=int,
                required=False,
                description="等待元素超时时间(秒)",
                default=10
            ),
            "retry": ActionParam(
                name="retry",
                type=bool,
                required=False,
                description="是否启用重试机制",
                default=True
            )
        }
    },
    
    ActionType.INPUT: {
        "description": "输入文本",
        "params": {
            "text": ActionParam(
                name="text",
                type=str,
                description="要输入的文本"
            ),
            "clear": ActionParam(
                name="clear",
                type=bool,
                required=False,
                description="是否先清空输入框",
                default=True
            )
        }
    },
    
    ActionType.SWIPE: {
        "description": "滑动屏幕",
        "params": {
            "direction": ActionParam(
                name="direction",
                type=str,
                description="滑动方向(up/down/left/right)"
            ),
            "duration": ActionParam(
                name="duration",
                type=float,
                required=False,
                description="滑动持续时间(秒)",
                default=0.5
            )
        }
    },
    
    ActionType.LAUNCH_APP: {
        "description": "启动应用",
        "params": {
            "package": ActionParam(
                name="package",
                type=str,
                description="应用包名"
            ),
            "wait_activity": ActionParam(
                name="wait_activity",
                type=str,
                required=False,
                description="等待出现的Activity名称"
            )
        }
    },
    
    ActionType.WAIT: {
        "description": "等待元素出现或指定时间",
        "params": {
            "target": ActionParam(
                name="target",
                type=str,
                required=False,
                description="等待的元素"
            ),
            "timeout": ActionParam(
                name="timeout",
                type=int,
                required=False,
                description="等待时间(秒)",
                default=10
            )
        }
    },
    
    ActionType.ASSERT: {
        "description": "断言元素存在或状态",
        "params": {
            "target": ActionParam(
                name="target",
                type=str,
                description="断言目标元素"
            ),
            "condition": ActionParam(
                name="condition",
                type=str,
                description="断言条件(exists/not_exists/contains_text)"
            ),
            "value": ActionParam(
                name="value",
                type=str,
                required=False,
                description="断言值"
            )
        }
    },
    
    ActionType.SEQUENCE: {
        "description": "按顺序执行多个动作",
        "params": {
            "actions": ActionParam(
                name="actions",
                type=list,
                description="要执行的动作列表"
            ),
            "continue_on_error": ActionParam(
                name="continue_on_error",
                type=bool,
                required=False,
                description="出错时是否继续执行",
                default=False
            )
        }
    },
    
    ActionType.PARALLEL: {
        "description": "并行执行多个动作",
        "params": {
            "actions": ActionParam(
                name="actions",
                type=list,
                description="要并行执行的动作列表"
            ),
            "timeout": ActionParam(
                name="timeout",
                type=int,
                required=False,
                description="总体超时时间(秒)",
                default=30
            )
        }
    },
    
    ActionType.CONDITIONAL: {
        "description": "条件执行",
        "params": {
            "condition": ActionParam(
                name="condition",
                type=dict,
                description="条件检查动作"
            ),
            "if_true": ActionParam(
                name="if_true",
                type=dict,
                description="条件为真时执行的动作"
            ),
            "if_false": ActionParam(
                name="if_false",
                type=dict,
                required=False,
                description="条件为假时执行的动作"
            )
        }
    },
    
    ActionType.LOOP: {
        "description": "循环执行动作",
        "params": {
            "action": ActionParam(
                name="action",
                type=dict,
                description="要循环执行的动作"
            ),
            "times": ActionParam(
                name="times",
                type=int,
                required=False,
                description="循环次数",
                default=None
            ),
            "until": ActionParam(
                name="until",
                type=dict,
                required=False,
                description="循环终止条件",
                default=None
            ),
            "max_iterations": ActionParam(
                name="max_iterations",
                type=int,
                required=False,
                description="最大循环次数",
                default=100
            )
        }
    }
}

class AutomationService:
    def __init__(self):
        self.devices = {}
        self.llm_service = LLMService()

    async def connect_device(self, device_id):
        """连接设备"""
        try:
            logger.info(f"Connecting to device: {device_id}")
            if device_id not in self.devices:
                device = u2.connect(device_id)
                # 开启uiautomator2的toast监控
                device.watcher.start()
                self.devices[device_id] = device
                logger.info(f"Successfully connected to device: {device_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect device {device_id}", exc_info=True,
                        extra={'device_id': device_id})
            raise DeviceError(f"Failed to connect device: {str(e)}")

    def validate_action(self, action: Dict) -> bool:
        """验证动作格式是否正确"""
        try:
            # 检查动作类型是否存在
            action_type = ActionType(action.get('type'))
            if action_type not in AVAILABLE_ACTIONS:
                raise AutomationError(f"Unknown action type: {action_type}")

            action_spec = AVAILABLE_ACTIONS[action_type]
            params = action.get('params', {})

            # 检查必需参数
            for param_name, param_spec in action_spec['params'].items():
                if param_spec.required and param_name not in params:
                    raise AutomationError(
                        f"Missing required parameter '{param_name}' for action '{action_type}'"
                    )

            # 检查参数类型
            for param_name, param_value in params.items():
                if param_name not in action_spec['params']:
                    raise AutomationError(
                        f"Unknown parameter '{param_name}' for action '{action_type}'"
                    )
                param_spec = action_spec['params'][param_name]
                if not isinstance(param_value, param_spec.type):
                    raise AutomationError(
                        f"Invalid type for parameter '{param_name}', "
                        f"expected {param_spec.type.__name__}"
                    )

            return True

        except ValueError as e:
            raise AutomationError(f"Invalid action: {str(e)}")
        except Exception as e:
            logger.error(f"Action validation failed: {str(e)}", exc_info=True)
            raise AutomationError(f"Action validation failed: {str(e)}")

    @retry_on_error(max_retries=3, delay=1)
    async def execute_action(self, device_id: str, action: Dict) -> bool:
        """执行自动化动作"""
        try:
            self.validate_action(action)
            device = self.devices.get(device_id)
            if not device:
                raise AutomationError("Device not connected")

            action_type = ActionType(action['type'])
            params = action.get('params', {})

            if action_type == ActionType.CLICK:
                # 使用动态点击替换静态点击
                return await self._execute_dynamic_click(
                    device,
                    params['target'],
                    fallback_to_text=params.get('fallback_to_text', True)
                )
            elif action_type == ActionType.INPUT:
                await self._execute_input(device, params)
            elif action_type == ActionType.SWIPE:
                await self._execute_swipe(device, params)
            elif action_type == ActionType.LAUNCH_APP:
                await self._execute_launch_app(device, params)
            elif action_type == ActionType.WAIT:
                await self._execute_wait(device, params)
            elif action_type == ActionType.ASSERT:
                await self._execute_assert(device, params)
            elif action_type == ActionType.SEQUENCE:
                return await self._execute_sequence(device_id, params)
            elif action_type == ActionType.PARALLEL:
                return await self._execute_parallel(device_id, params)
            elif action_type == ActionType.CONDITIONAL:
                return await self._execute_conditional(device_id, params)
            elif action_type == ActionType.LOOP:
                return await self._execute_loop(device_id, params)
            else:
                raise AutomationError(f"Unsupported action type: {action_type}")

        except Exception as e:
            logger.error(
                f"Action execution failed: {str(e)}", 
                exc_info=True,
                extra={'device_id': device_id}
            )
            raise AutomationError(f"Action execution failed: {str(e)}")

    async def _execute_sequence(self, device_id: str, params: Dict) -> bool:
        """按顺序执行多个动作"""
        actions = params['actions']
        continue_on_error = params.get('continue_on_error', False)
        
        for action in actions:
            try:
                await self.execute_action(device_id, action)
            except Exception as e:
                if not continue_on_error:
                    raise
                logger.warning(f"Action failed but continuing: {str(e)}")
        return True

    async def _execute_parallel(self, device_id: str, params: Dict) -> bool:
        """并行执行多个动作"""
        actions = params['actions']
        timeout = params.get('timeout', 30)
        
        tasks = [
            self.execute_action(device_id, action)
            for action in actions
        ]
        
        try:
            await asyncio.gather(*tasks, timeout=timeout)
            return True
        except asyncio.TimeoutError:
            raise AutomationError(f"Parallel execution timed out after {timeout}s")

    async def _execute_conditional(self, device_id: str, params: Dict) -> bool:
        """条件执行"""
        try:
            # 执行条件检查
            condition_result = await self.execute_action(
                device_id, 
                params['condition']
            )
            
            # 根据条件结果选择执行路径
            if condition_result:
                return await self.execute_action(device_id, params['if_true'])
            elif 'if_false' in params:
                return await self.execute_action(device_id, params['if_false'])
            return True
            
        except Exception as e:
            raise AutomationError(f"Conditional execution failed: {str(e)}")

    async def _execute_loop(self, device_id: str, params: Dict) -> bool:
        """循环执行"""
        action = params['action']
        times = params.get('times')
        until = params.get('until')
        max_iterations = params.get('max_iterations', 100)
        
        iteration = 0
        while True:
            # 检查最大循环次数
            if iteration >= max_iterations:
                raise AutomationError(f"Loop exceeded maximum iterations ({max_iterations})")
                
            # 执行动作
            await self.execute_action(device_id, action)
            iteration += 1
            
            # 检查终止条件
            if times and iteration >= times:
                break
            if until:
                try:
                    condition_met = await self.execute_action(device_id, until)
                    if condition_met:
                        break
                except Exception as e:
                    logger.warning(f"Loop condition check failed: {str(e)}")
                    
        return True

    @retry_on_error(max_retries=3, delay=1)
    async def _execute_basic_action(self, device, action_type: ActionType, params: Dict) -> bool:
        """执行基础动作（带重试）"""
        # 执行相应的基础动作
        if action_type == ActionType.CLICK:
            await self._execute_click(device, params)
        elif action_type == ActionType.INPUT:
            await self._execute_input(device, params)
        elif action_type == ActionType.SWIPE:
            await self._execute_swipe(device, params)
        elif action_type == ActionType.LAUNCH_APP:
            await self._execute_launch_app(device, params)
        elif action_type == ActionType.WAIT:
            await self._execute_wait(device, params)
        elif action_type == ActionType.ASSERT:
            await self._execute_assert(device, params)
        else:
            raise AutomationError(f"Unsupported action type: {action_type}")
        return True

    async def _execute_click(self, device, params):
        """执行点击操作"""
        target = params['target']
        timeout = params.get('timeout', 10)
        
        # 等待元素出现
        element = await device(text=target).wait(timeout=timeout)
        if not element:
            raise AutomationError(f"Element not found: {target}")
            
        # 执行点击
        element.click()

    async def _execute_input(self, device, params):
        """执行输入操作"""
        text = params['text']
        clear = params.get('clear', True)
        
        if clear:
            device.clear_text()
        device.send_keys(text)

    async def _execute_swipe(self, device, params):
        """执行滑动操作"""
        direction = params['direction']
        duration = params.get('duration', 0.5)
        
        # 获取屏幕尺寸
        screen_size = device.window_size()
        width, height = screen_size[0], screen_size[1]
        
        # 计算滑动坐标
        if direction == 'up':
            start = (width/2, height*0.8)
            end = (width/2, height*0.2)
        elif direction == 'down':
            start = (width/2, height*0.2)
            end = (width/2, height*0.8)
        elif direction == 'left':
            start = (width*0.8, height/2)
            end = (width*0.2, height/2)
        elif direction == 'right':
            start = (width*0.2, height/2)
            end = (width*0.8, height/2)
        else:
            raise AutomationError(f"Invalid swipe direction: {direction}")
            
        device.swipe(start, end, duration=duration)

    async def _execute_launch_app(self, device, params):
        """执行启动应用操作"""
        package = params['package']
        wait_activity = params.get('wait_activity')
        
        device.app_start(package)
        if wait_activity:
            device.wait_activity(wait_activity, timeout=10)

    async def _execute_wait(self, device, params):
        """执行等待操作"""
        target = params.get('target')
        timeout = params.get('timeout', 10)
        
        if target:
            element = await device(text=target).wait(timeout=timeout)
            if not element:
                raise AutomationError(f"Element not found after waiting: {target}")
        else:
            await asyncio.sleep(timeout)

    async def _execute_assert(self, device, params):
        """执行断言操作"""
        target = params['target']
        condition = params['condition']
        value = params.get('value')
        
        element = device(text=target)
        
        if condition == 'exists':
            if not element.exists:
                raise AutomationError(f"Assert failed: element '{target}' does not exist")
        elif condition == 'not_exists':
            if element.exists:
                raise AutomationError(f"Assert failed: element '{target}' exists")
        elif condition == 'contains_text':
            if not value or value not in element.text:
                raise AutomationError(f"Assert failed: element '{target}' does not contain text '{value}'")
        else:
            raise AutomationError(f"Invalid assert condition: {condition}")

    async def disconnect_device(self, device_id):
        """断开设备连接"""
        try:
            if device_id in self.devices:
                device = self.devices[device_id]
                device.disconnect()
                del self.devices[device_id]
            return True
        except Exception as e:
            logger.error(f"Failed to disconnect device {device_id}: {str(e)}")
            return False

    def get_device_info(self, device_id):
        """获取设备信息"""
        try:
            device = self.devices.get(device_id)
            if device:
                info = device.info
                return {
                    'connected': True,
                    'resolution': [info['displayWidth'], info['displayHeight']],
                    'orientation': info['displayRotation'],
                    'sdk_version': info['sdkInt'],
                    'serial': device_id,
                    'current_app': device.app_current()
                }
            return {'connected': False}
        except Exception as e:
            logger.error(f"Failed to get device info: {str(e)}")
            return {'connected': False, 'error': str(e)}

    def setup_watchers(self, device_id):
        """设置自动化监控"""
        device = self.devices.get(device_id)
        if device:
            # 监控常见弹窗
            device.watcher.when("允许").click()
            device.watcher.when("确定").click()
            device.watcher.when("同意").click()
            
            # 监控应用崩溃
            device.watcher.when("应用停止运行").when("确定").click()
            
            # 开启监控
            device.watcher.start()

    async def _capture_screen(self, device) -> str:
        """捕获屏幕并转换为base64"""
        try:
            # 截图并转换为PIL Image
            screenshot = device.screenshot()
            img = Image.open(BytesIO(screenshot))
            
            # 转换为base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
            
        except Exception as e:
            logger.error(f"Failed to capture screen: {str(e)}", exc_info=True)
            raise AutomationError(f"Screenshot failed: {str(e)}")

    async def _find_element_with_vision(
        self, 
        device, 
        target: str,
        element_type: str = "button",
        max_retries: int = 3,
        confidence_threshold: float = 0.7
    ) -> Optional[Dict]:
        """使用视觉模型查找元素"""
        for attempt in range(max_retries):
            try:
                # 捕获屏幕
                screen_base64 = await self._capture_screen(device)
                
                # 构建视觉查询
                query = f"""
                在这个Android应用界面截图中，请帮我找到"{target}"{element_type}。
                返回格式：
                {{
                    "found": true/false,
                    "confidence": 0.0-1.0,
                    "box": [x1, y1, x2, y2],  // 左上角和右下角坐标
                    "description": "元素位置描述"
                }}
                """
                
                # 调用视觉模型
                result = await self.llm_service.analyze_image(
                    image_base64=screen_base64,
                    query=query
                )
                
                if result.get('found') and result.get('confidence', 0) >= confidence_threshold:
                    return result
                    
                if attempt < max_retries - 1:
                    # 在重试前滑动屏幕
                    device.swipe(0.5, 0.8, 0.5, 0.2)  # 向上滑动
                    await asyncio.sleep(1)  # 等待UI更新
                    
            except Exception as e:
                logger.warning(f"Vision analysis attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise AutomationError(f"Vision analysis failed: {str(e)}")
                
        return None

    async def _execute_dynamic_click(
        self, 
        device, 
        target: str,
        fallback_to_text: bool = True
    ) -> bool:
        """执行动态点击"""
        try:
            # 首先尝试使用视觉模型
            element = await self._find_element_with_vision(device, target)
            
            if element and element.get('found'):
                # 使用边界框中心点进行点击
                box = element['box']
                center_x = (box[0] + box[2]) / 2
                center_y = (box[1] + box[3]) / 2
                device.click(center_x, center_y)
                return True
                
            # 如果视觉识别失败，尝试传统文本匹配
            if fallback_to_text:
                logger.info(f"Vision-based click failed, falling back to text-based search for '{target}'")
                element = device(text=target)
                if element.exists:
                    element.click()
                    return True
                    
            raise AutomationError(f"Failed to find and click element: {target}")
            
        except Exception as e:
            logger.error(f"Dynamic click failed: {str(e)}", exc_info=True)
            raise AutomationError(f"Click operation failed: {str(e)}")

# 确保导出 AutomationService 类
__all__ = ['AutomationService']
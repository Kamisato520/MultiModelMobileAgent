import aiohttp
import json
from app.config import Config
import base64
from typing import List, Dict, Optional
from app.utils.exceptions import LLMError
from app.utils.logger import logger
from app.utils.cache import cache_llm_response
from app.utils.monitoring import monitor_llm_call
from app.services.automation_service import AVAILABLE_ACTIONS, ActionType
from app.utils.response import ResponseAnalyzer, log_validation_errors
from app.models.device import Device
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from app.models.task import Task, TaskResult
from app.utils.cache import cache

class PromptOptimizer:
    """提示词优化器"""
    def __init__(self):
        self.success_patterns = defaultdict(int)  # 成功模式统计
        self.failure_patterns = defaultdict(int)  # 失败模式统计
        self.template_performance = defaultdict(list)  # 模板性能统计

    def analyze_task_results(self, tasks: List[Task], window_days: int = 7):
        """分析任务执行结果"""
        cutoff_date = datetime.utcnow() - timedelta(days=window_days)
        
        for task in tasks:
            if task.end_time and task.end_time > cutoff_date:
                # 分析成功/失败模式
                if task.result == TaskResult.SUCCESS:
                    self._analyze_success_pattern(task)
                else:
                    self._analyze_failure_pattern(task)
                
                # 记录模板性能
                if task.prompt_template:
                    self.template_performance[task.prompt_template].append({
                        'success': task.result == TaskResult.SUCCESS,
                        'duration': task.execution_duration,
                        'retry_count': task.retry_count
                    })

    def _analyze_success_pattern(self, task: Task):
        """分析成功模式"""
        # 提取关键特征
        features = {
            'step_count': len(task.execution_steps),
            'action_types': [step['type'] for step in task.execution_steps],
            'execution_duration': task.execution_duration,
            'retry_count': task.retry_count
        }
        
        # 生成模式指纹
        pattern_key = json.dumps(features, sort_keys=True)
        self.success_patterns[pattern_key] += 1

    def _analyze_failure_pattern(self, task: Task):
        """分析失败模式"""
        features = {
            'result': task.result.value,
            'error_type': task.error_message[:50] if task.error_message else None,
            'failed_step': next(
                (i for i, r in enumerate(task.step_results or []) if not r['success']),
                None
            )
        }
        
        pattern_key = json.dumps(features, sort_keys=True)
        self.failure_patterns[pattern_key] += 1

    def get_optimization_suggestions(self) -> Dict:
        """获取优化建议"""
        suggestions = {
            'prompt_templates': {},
            'common_failures': [],
            'success_patterns': []
        }
        
        # 分析模板性能
        for template, results in self.template_performance.items():
            success_rate = sum(1 for r in results if r['success']) / len(results)
            avg_duration = np.mean([r['duration'] for r in results])
            avg_retries = np.mean([r['retry_count'] for r in results])
            
            suggestions['prompt_templates'][template] = {
                'success_rate': success_rate,
                'avg_duration': avg_duration,
                'avg_retries': avg_retries,
                'sample_size': len(results)
            }
        
        # 分析常见失败
        for pattern, count in sorted(
            self.failure_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]:
            suggestions['common_failures'].append({
                'pattern': json.loads(pattern),
                'count': count
            })
        
        # 分析成功模式
        for pattern, count in sorted(
            self.success_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]:
            suggestions['success_patterns'].append({
                'pattern': json.loads(pattern),
                'count': count
            })
        
        return suggestions

class DialogueContext:
    """对话上下文管理"""
    def __init__(self, context_id: str, max_history: int = 5):
        self.context_id = context_id
        self.max_history = max_history
        self.tasks = []
        self.variables = {}  # 上下文变量
        self.last_update = datetime.utcnow()

    def add_task(self, task: Task):
        """添加任务到上下文"""
        self.tasks.append(task)
        if len(self.tasks) > self.max_history:
            self.tasks.pop(0)
        self.last_update = datetime.utcnow()

    def get_context_summary(self) -> str:
        """生成上下文摘要"""
        if not self.tasks:
            return ""
            
        summary = "之前的操作：\n"
        for task in self.tasks:
            result = "成功" if task.result == TaskResult.SUCCESS else "失败"
            summary += f"- 指令：{task.user_input} ({result})\n"
            
        summary += f"\n上下文变量：\n"
        for key, value in self.variables.items():
            summary += f"- {key}: {value}\n"
            
        return summary

class LLMService:
    def __init__(self):
        self.api_key = Config.DASHSCOPE_API_KEY
        self.text_model = Config.MODELS['text']
        self.vision_model = Config.MODELS['vision']
        self.response_analyzer = ResponseAnalyzer()
        self.max_retries = 3
        self.prompt_optimizer = PromptOptimizer()
        self.contexts = {}  # 对话上下文缓存

    def _generate_action_description(self) -> str:
        """生成动作描述文本"""
        descriptions = []
        for action_type, spec in AVAILABLE_ACTIONS.items():
            params_desc = []
            for param_name, param in spec['params'].items():
                required = "必需" if param.required else "可选"
                default = f"，默认值：{param.default}" if param.default is not None else ""
                params_desc.append(
                    f"- {param_name}: {param.description} ({required}{default})"
                )
            
            descriptions.append(
                f"\n{action_type.value}：{spec['description']}\n"
                f"参数：\n" + "\n".join(params_desc)
            )
        
        return "\n".join(descriptions)

    def _generate_examples(self) -> str:
        """生成示例输入输出对"""
        return """
示例1：
用户说：打开微信，找到张三发送"在吗？"
输出：[
    {
        "type": "launch_app",
        "params": {
            "package": "com.tencent.mm"
        }
    },
    {
        "type": "click",
        "params": {
            "target": "通讯录"
        }
    },
    {
        "type": "input",
        "params": {
            "text": "张三"
        }
    },
    {
        "type": "click",
        "params": {
            "target": "张三"
        }
    },
    {
        "type": "input",
        "params": {
            "text": "在吗？"
        }
    },
    {
        "type": "click",
        "params": {
            "target": "发送"
        }
    }
]

示例2：
用户说：滑动查找"订单记录"按钮然后点击
输出：[
    {
        "type": "loop",
        "params": {
            "action": {
                "type": "swipe",
                "params": {
                    "direction": "up",
                    "duration": 0.5
                }
            },
            "until": {
                "type": "assert",
                "params": {
                    "target": "订单记录",
                    "condition": "exists"
                }
            },
            "max_iterations": 5
        }
    },
    {
        "type": "click",
        "params": {
            "target": "订单记录"
        }
    }
]

示例3：
用户说：如果看到"同意"按钮就点击，否则点击"跳过"
输出：[
    {
        "type": "conditional",
        "params": {
            "condition": {
                "type": "assert",
                "params": {
                    "target": "同意",
                    "condition": "exists"
                }
            },
            "if_true": {
                "type": "click",
                "params": {
                    "target": "同意"
                }
            },
            "if_false": {
                "type": "click",
                "params": {
                    "target": "跳过"
                }
            }
        }
    }
]

示例4：
用户说：等待支付结果，成功后截图保存
输出：[
    {
        "type": "sequence",
        "params": {
            "actions": [
                {
                    "type": "wait",
                    "params": {
                        "target": "支付成功",
                        "timeout": 30
                    }
                },
                {
                    "type": "screenshot",
                    "params": {
                        "filename": "payment_success"
                    }
                }
            ]
        }
    }
]
"""

    def _generate_device_context(self, device: Device) -> str:
        """生成设备上下文描述"""
        constraints = device.get_automation_constraints()
        
        if not constraints['supported']:
            return f"注意：当前设备({device.name})不支持自动化操作。原因：{constraints['reason']}"
            
        capabilities = device.capabilities
        context = f"""
设备信息：
- 平台：Android {device.platform_version}
- 设备名称：{device.name}
- 自动化框架：uiautomator2

设备支持的功能：
- 触摸操作：{'支持' if capabilities['supports_touch'] else '不支持'}
- 文本输入：{'支持' if capabilities['supports_input'] else '不支持'}
- 手势操作：{'支持' if capabilities['supports_gestures'] else '不支持'}
- 屏幕截图：{'支持' if capabilities['supports_screenshot'] else '不支持'}

注意事项：
1. 所有操作都基于Android原生UI自动化
2. 需要确保目标元素在屏幕上可见
3. 某些操作可能需要特定系统权限
"""
        return context

    def _generate_prompt(self, text: str, device: Device, context_summary: Optional[str] = None) -> str:
        """生成完整的提示词"""
        device_context = self._generate_device_context(device)
        
        if not device.is_automation_supported():
            return f"""
{device_context}

由于设备限制，无法执行自动化操作。请检查设备类型和状态，或选择支持的设备。
"""
        
        return f"""你是一个Android设备自动化助手，负责将用户的自然语言指令转换为结构化的自动化操作序列。

{device_context}

可用的自动化动作如下：
{self._generate_action_description()}

请注意：
1. 所有操作都是基于Android设备的uiautomator2框架
2. 输出必须是合法的JSON格式
3. 每个动作必须包含type和params两个字段
4. 参数必须符合动作的定义要求
5. 可以使用sequence、parallel、conditional、loop等组合动作
6. 优先使用组合动作来处理复杂场景
7. 确保每个必需参数都已提供
8. 参数值类型必须正确（如数字、字符串、布尔值等）

以下是一些示例：
{self._generate_examples()}

现在，请将以下用户指令转换为自动化操作序列：
{text}

请仅输出JSON格式的操作序列，不需要其他解释。

上下文：
{context_summary}
"""

    def _get_or_create_context(self, context_id: str) -> DialogueContext:
        """获取或创建对话上下文"""
        if context_id not in self.contexts:
            self.contexts[context_id] = DialogueContext(context_id)
        return self.contexts[context_id]

    def _clean_expired_contexts(self, max_age_hours: int = 24):
        """清理过期的上下文"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        self.contexts = {
            k: v for k, v in self.contexts.items()
            if v.last_update > cutoff_time
        }

    @monitor_llm_call
    @cache_llm_response(timeout=300)
    async def analyze_text_input(
        self,
        text: str,
        device: Device,
        context_id: Optional[str] = None
    ) -> List[Dict]:
        """分析文本输入并生成执行步骤"""
        try:
            # 获取上下文
            context = None
            if context_id:
                context = self._get_or_create_context(context_id)
                
            # 构建提示词
            prompt = self._generate_prompt(
                text,
                device,
                context.get_context_summary() if context else None
            )
            
            # 调用LLM API并处理响应
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    json={
                        'model': self.text_model,
                        'input': {
                            'prompt': prompt
                        },
                        'parameters': {
                            'temperature': 0.2,
                            'top_p': 0.9,
                            'result_format': 'json'
                        }
                    }
                ) as response:
                    result = await response.json()
                    
                    if response.status != 200:
                        raise LLMError(f"LLM API error: {result.get('message')}")
                    
                    # 验证响应
                    content = result['output']['choices'][0]['message']['content']
                    validation_report = self.response_analyzer.analyze_response(
                        content,
                        AVAILABLE_ACTIONS
                    )
                    
                    if not validation_report['is_valid']:
                        log_validation_errors(validation_report['errors'])
                        raise LLMError(
                            "Invalid automation sequence",
                            validation_report
                        )
                    
                    actions = json.loads(content)
                    
            # 更新上下文
            if context:
                context.variables.update(self._extract_variables(text))
            
            return actions
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}", exc_info=True)
            raise LLMError(f"Failed to analyze input: {str(e)}")

    def _extract_variables(self, text: str) -> Dict:
        """从用户输入中提取上下文变量"""
        # 简单的变量提取示例
        variables = {}
        # 提取联系人名称
        if "联系人" in text:
            import re
            match = re.search(r"联系人[：:]\s*(\w+)", text)
            if match:
                variables['contact_name'] = match.group(1)
        return variables

    def _adjust_prompt_for_retry(self, text: str, validation_report: Dict) -> str:
        """根据验证错误调整提示词"""
        error_types = validation_report['summary']['error_types']
        
        additional_instructions = []
        if 'invalid_json' in error_types:
            additional_instructions.append(
                "请确保输出是有效的JSON数组格式。"
            )
        if 'invalid_action' in error_types:
            additional_instructions.append(
                f"请只使用以下动作类型：{', '.join([a.value for a in AVAILABLE_ACTIONS])}"
            )
        if 'missing_param' in error_types or 'invalid_type' in error_types:
            additional_instructions.append(
                "请确保提供所有必需参数，并使用正确的参数类型。"
            )
            
        if additional_instructions:
            text += "\n\n注意：" + " ".join(additional_instructions)
            
        return text

    async def _call_llm_api(self, text: str) -> Dict:
        """调用LLM API"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
                headers={'Authorization': f'Bearer {self.api_key}'},
                json={
                    'model': self.text_model,
                    'input': {
                        'prompt': self._generate_prompt(text)
                    },
                    'parameters': {
                        'temperature': 0.2,
                        'top_p': 0.9,
                        'result_format': 'json'
                    }
                }
            ) as response:
                if response.status != 200:
                    raise LLMError(f"API request failed: {response.status}")
                return await response.json()

    def _parse_llm_response(self, result: Dict) -> List[Dict]:
        """解析LLM响应"""
        try:
            content = result['output']['choices'][0]['message']['content']
            # 尝试直接解析JSON
            import json
            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            raise LLMError("Invalid response format")

    def _validate_actions(self, actions: List[Dict]) -> None:
        """验证动作列表的合法性"""
        from app.services.automation_service import AutomationService
        automation_service = AutomationService()
        
        def validate_action(action):
            if not isinstance(action, dict):
                raise LLMError("Action must be a dictionary")
            if 'type' not in action:
                raise LLMError("Action must have 'type' field")
            if 'params' not in action:
                raise LLMError("Action must have 'params' field")
            
            # 验证动作格式
            automation_service.validate_action(action)
            
            # 递归验证组合动作
            params = action['params']
            if action['type'] == 'sequence':
                for sub_action in params.get('actions', []):
                    validate_action(sub_action)
            elif action['type'] == 'parallel':
                for sub_action in params.get('actions', []):
                    validate_action(sub_action)
            elif action['type'] == 'conditional':
                if 'condition' in params:
                    validate_action(params['condition'])
                if 'if_true' in params:
                    validate_action(params['if_true'])
                if 'if_false' in params:
                    validate_action(params['if_false'])
            elif action['type'] == 'loop':
                if 'action' in params:
                    validate_action(params['action'])
                if 'until' in params:
                    validate_action(params['until'])
        
        for action in actions:
            validate_action(action)

    async def analyze_audio_input(self, audio_file_path: str) -> list:
        """使用qwen-audio-turbo分析语音输入"""
        payload = {
            "model": self.text_model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"audio": audio_file_path},
                            {"text": "请分析这段语音并转换为自动化执行步骤"}
                        ]
                    }
                ]
            }
        }
        
        result = await self._make_request('audio', payload)
        return self._parse_audio_response(result)

    async def perform_ocr(self, image_path: str) -> dict:
        """使用qwen-vl-ocr进行OCR识别"""
        payload = {
            "model": self.text_model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": image_path},
                            {"text": "请识别图片中的文字"}
                        ]
                    }
                ]
            }
        }
        
        result = await self._make_request('ocr', payload)
        return self._parse_ocr_response(result)

    async def analyze_screen(self, screenshot_path: str) -> dict:
        """使用qwen-vl-max分析屏幕截图"""
        payload = {
            "model": self.text_model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": screenshot_path},
                            {"text": "分析屏幕上的UI元素位置和功能"}
                        ]
                    }
                ]
            }
        }
        
        result = await self._make_request('vision', payload)
        return self._parse_vision_response(result)

    def _parse_text_response(self, response: dict) -> list:
        """解析文本模型响应"""
        try:
            steps = []
            if 'output' in response and 'choices' in response['output']:
                content = response['output']['choices'][0]['message']['content']
                # 解析返回的内容为执行步骤
                # 这里需要根据实际返回格式调整解析逻辑
                return self._convert_to_execution_steps(content)
            return steps
        except Exception as e:
            raise Exception(f"Failed to parse text response: {str(e)}")

    def _parse_audio_response(self, response: dict) -> list:
        """解析语音模型响应"""
        try:
            if 'output' in response and 'choices' in response['output']:
                text_content = response['output']['choices'][0]['message']['content'][0]['text']
                # 将识别出的文本转换为执行步骤
                return self._convert_to_execution_steps(text_content)
            return []
        except Exception as e:
            raise Exception(f"Failed to parse audio response: {str(e)}")

    def _convert_to_execution_steps(self, content: str) -> list:
        """将模型返回的内容转换为可执行步骤"""
        # 示例转换逻辑
        steps = []
        
        # 解析内容中的指令
        instructions = content.split('\n')
        for instruction in instructions:
            if '点击' in instruction:
                steps.append({
                    'type': 'click',
                    'params': {'text': instruction.split('点击')[-1].strip()}
                })
            elif '输入' in instruction:
                steps.append({
                    'type': 'input',
                    'params': {'text': instruction.split('输入')[-1].strip()}
                })
            elif '启动应用' in instruction:
                steps.append({
                    'type': 'app_start',
                    'params': {'package': instruction.split('启动应用')[-1].strip()}
                })
            elif '滑动' in instruction:
                direction = instruction.split('滑动')[-1].strip()
                if direction == '上':
                    steps.append({
                        'type': 'swipe',
                        'params': {'direction': [0.5, 0.8, 0.5, 0.2]}
                    })
                # 添加其他方向的滑动支持
                
        return steps

    @monitor_llm_call
    @cache_llm_response(timeout=60)  # 较短的缓存时间，因为UI可能变化
    async def analyze_image(
        self,
        image_base64: str,
        query: str,
        temperature: float = 0.2
    ) -> Dict:
        """分析图像并定位UI元素"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation',
                    headers={'Authorization': f'Bearer {self.api_key}'},
                    json={
                        'model': self.vision_model,
                        'input': {
                            'prompt': query,
                            'image': image_base64
                        },
                        'parameters': {
                            'temperature': temperature,
                            'result_format': 'json'
                        }
                    }
                ) as response:
                    result = await response.json()
                    
                    if response.status != 200:
                        raise LLMError(f"Vision API error: {result.get('message')}")
                    
                    try:
                        # 解析并验证响应
                        content = result['output']['choices'][0]['message']['content']
                        response_data = json.loads(content)
                        
                        # 验证响应格式
                        required_fields = ['found', 'confidence', 'box']
                        if not all(field in response_data for field in required_fields):
                            raise LLMError("Invalid vision analysis response format")
                            
                        # 验证坐标值
                        box = response_data['box']
                        if len(box) != 4 or not all(isinstance(x, (int, float)) for x in box):
                            raise LLMError("Invalid bounding box coordinates")
                            
                        return response_data
                        
                    except json.JSONDecodeError:
                        raise LLMError("Invalid JSON response from vision model")
                    except Exception as e:
                        raise LLMError(f"Failed to parse vision analysis response: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Vision analysis failed: {str(e)}", exc_info=True)
            raise LLMError(f"Failed to analyze image: {str(e)}")

    async def optimize_prompts(self):
        """定期优化提示词"""
        # 获取最近的任务
        recent_tasks = Task.query.filter(
            Task.end_time > datetime.utcnow() - timedelta(days=7)
        ).all()
        
        # 分析任务结果
        self.prompt_optimizer.analyze_task_results(recent_tasks)
        
        # 获取优化建议
        suggestions = self.prompt_optimizer.get_optimization_suggestions()
        
        # 记录分析结果
        logger.info("Prompt optimization suggestions:", extra={
            'suggestions': suggestions
        })
        
        return suggestions

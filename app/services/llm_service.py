import aiohttp
import json
from app.config import Config
import base64

class LLMService:
    def __init__(self):
        self.api_key = Config.DASHSCOPE_API_KEY
        self.models = Config.MODELS

    async def _make_request(self, model_type, payload):
        """通用的API请求方法"""
        model_config = self.models[model_type]
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                model_config['api_url'],
                json=payload,
                headers=headers
            ) as response:
                return await response.json()

    async def analyze_text_input(self, text: str) -> list:
        """使用qwen-plus分析文本输入"""
        payload = {
            "model": self.models['text']['name'],
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an automation expert. Convert user instructions into executable steps."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            }
        }
        
        result = await self._make_request('text', payload)
        return self._parse_text_response(result)

    async def analyze_audio_input(self, audio_file_path: str) -> list:
        """使用qwen-audio-turbo分析语音输入"""
        payload = {
            "model": self.models['audio']['name'],
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
            "model": self.models['ocr']['name'],
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
            "model": self.models['vision']['name'],
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
        # 这里需要实现具体的转换逻辑
        # 返回格式示例:
        return [
            {
                "type": "touch",
                "params": {"image": "target.png"}
            },
            {
                "type": "text",
                "params": {"content": "input text"}
            }
        ]

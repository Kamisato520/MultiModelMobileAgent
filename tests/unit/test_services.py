import pytest
from unittest.mock import Mock, patch
from app.services.automation_service import AutomationService
from app.services.llm_service import LLMService
from app.utils.exceptions import DeviceError

@pytest.fixture
def automation_service():
    return AutomationService()

@pytest.fixture
def llm_service():
    return LLMService()

@pytest.mark.asyncio
async def test_connect_device(automation_service):
    """测试设备连接"""
    with patch('uiautomator2.connect') as mock_connect:
        mock_device = Mock()
        mock_connect.return_value = mock_device
        
        result = await automation_service.connect_device('test_device')
        assert result is True
        mock_connect.assert_called_once_with('test_device')

@pytest.mark.asyncio
async def test_execute_action(automation_service):
    """测试执行自动化操作"""
    with patch.dict(automation_service.devices, {'test_device': Mock()}):
        action = {
            'type': 'click',
            'params': {'text': 'Button'}
        }
        result = await automation_service.execute_action('test_device', action)
        assert result is True

@pytest.mark.asyncio
async def test_analyze_text_input(llm_service):
    """测试文本分析"""
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json.return_value = {
            'output': {
                'choices': [{
                    'message': {'content': 'Click Button A\nInput Text'}
                }]
            }
        }
        
        result = await llm_service.analyze_text_input('test input')
        assert isinstance(result, list)
        assert len(result) > 0 
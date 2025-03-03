from flask import jsonify
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import json
from app.utils.logger import logger

@dataclass
class ValidationError:
    """验证错误信息"""
    error_type: str
    message: str
    location: Optional[str] = None
    details: Optional[Dict] = None

class ResponseValidator:
    """LLM响应验证器"""
    
    @staticmethod
    def validate_json(content: str) -> Union[List[Dict], ValidationError]:
        """验证JSON格式"""
        try:
            data = json.loads(content)
            if not isinstance(data, list):
                return ValidationError(
                    error_type="invalid_format",
                    message="Response must be a JSON array",
                    details={"received_type": type(data).__name__}
                )
            return data
        except json.JSONDecodeError as e:
            return ValidationError(
                error_type="invalid_json",
                message="Invalid JSON format",
                location=str(e.pos),
                details={"error": str(e)}
            )

    @staticmethod
    def validate_action_type(action: Dict, available_actions: Dict) -> Optional[ValidationError]:
        """验证动作类型"""
        if 'type' not in action:
            return ValidationError(
                error_type="missing_field",
                message="Action missing 'type' field",
                details={"action": action}
            )
            
        action_type = action['type']
        if action_type not in [a.value for a in available_actions]:
            return ValidationError(
                error_type="invalid_action",
                message=f"Unknown action type: {action_type}",
                details={
                    "action": action,
                    "available_actions": [a.value for a in available_actions]
                }
            )
        return None

    @staticmethod
    def validate_params(action: Dict, action_spec: Dict) -> Optional[ValidationError]:
        """验证动作参数"""
        if 'params' not in action:
            return ValidationError(
                error_type="missing_field",
                message="Action missing 'params' field",
                details={"action": action}
            )
            
        params = action['params']
        spec_params = action_spec['params']
        
        # 检查必需参数
        for param_name, param_spec in spec_params.items():
            if param_spec.required and param_name not in params:
                return ValidationError(
                    error_type="missing_param",
                    message=f"Missing required parameter: {param_name}",
                    details={
                        "action": action,
                        "param_spec": param_spec.__dict__
                    }
                )
            
            # 检查参数类型
            if param_name in params:
                param_value = params[param_name]
                if not isinstance(param_value, param_spec.type):
                    return ValidationError(
                        error_type="invalid_type",
                        message=f"Invalid type for parameter {param_name}",
                        details={
                            "expected": param_spec.type.__name__,
                            "received": type(param_value).__name__,
                            "value": param_value
                        }
                    )
                
                # 执行自定义验证
                if param_spec.validator:
                    try:
                        param_spec.validator(param_value)
                    except Exception as e:
                        return ValidationError(
                            error_type="validation_failed",
                            message=f"Validation failed for parameter {param_name}",
                            details={"error": str(e)}
                        )
        
        # 检查未知参数
        unknown_params = set(params.keys()) - set(spec_params.keys())
        if unknown_params:
            return ValidationError(
                error_type="unknown_params",
                message="Unknown parameters found",
                details={"unknown_params": list(unknown_params)}
            )
            
        return None

class ResponseAnalyzer:
    """LLM响应分析器"""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        
    def analyze_response(self, content: str, available_actions: Dict) -> Dict:
        """分析LLM响应"""
        self.errors = []
        
        # 验证JSON格式
        result = ResponseValidator.validate_json(content)
        if isinstance(result, ValidationError):
            self.errors.append(result)
            return self._generate_report()
            
        actions = result
        
        # 验证每个动作
        for i, action in enumerate(actions):
            # 验证动作类型
            error = ResponseValidator.validate_action_type(action, available_actions)
            if error:
                error.location = f"action[{i}]"
                self.errors.append(error)
                continue
                
            # 验证动作参数
            action_type = action['type']
            action_spec = available_actions[action_type]
            error = ResponseValidator.validate_params(action, action_spec)
            if error:
                error.location = f"action[{i}].params"
                self.errors.append(error)
        
        return self._generate_report()
    
    def _generate_report(self) -> Dict:
        """生成验证报告"""
        report = {
            'is_valid': len(self.errors) == 0,
            'error_count': len(self.errors),
            'errors': [error.__dict__ for error in self.errors]
        }
        
        if self.errors:
            error_types = [error.error_type for error in self.errors]
            report['summary'] = {
                'error_types': list(set(error_types)),
                'most_common_error': max(set(error_types), key=error_types.count)
            }
            
        return report

def log_validation_errors(errors: List[ValidationError]) -> None:
    """记录验证错误"""
    for error in errors:
        log_message = f"Validation error: {error.error_type} - {error.message}"
        if error.location:
            log_message += f" at {error.location}"
        if error.details:
            log_message += f"\nDetails: {json.dumps(error.details, indent=2)}"
        logger.error(log_message)

def success_response(data=None, message="Success"):
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response)

def error_response(message="Error", code=400):
    return jsonify({
        "success": False,
        "message": message
    }), code

def validation_error(errors):
    return jsonify({
        "success": False,
        "message": "Validation error",
        "errors": errors
    }), 422

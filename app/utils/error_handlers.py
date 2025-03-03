from flask import jsonify
from .exceptions import AutomationError, format_error_response
from .logger import logger

def register_error_handlers(app):
    """注册全局错误处理器"""
    
    @app.errorhandler(AutomationError)
    def handle_automation_error(error):
        logger.error(f"Automation error: {str(error)}", exc_info=True)
        return jsonify(format_error_response(error)), 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        logger.warning(f"Not found: {str(error)}")
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def handle_server_error(error):
        logger.error(f"Server error: {str(error)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500 
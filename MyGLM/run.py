import asyncio
import websockets
from app import create_app
from app.services.websocket_service import WebSocketService
from app.config import Config
import logging
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用和WebSocket服务
app = create_app()
websocket_service = WebSocketService()

async def start_websocket_server():
    """启动WebSocket服务器"""
    try:
        server = await websockets.serve(
            websocket_service.handle_connection,
            "127.0.0.1",
            Config.WEBSOCKET_PORT
        )
        logger.info(f"WebSocket server started on port {Config.WEBSOCKET_PORT}")
        await server.wait_closed()
    except Exception as e:
        logger.error(f"Failed to start WebSocket server: {str(e)}")
        raise

async def start_flask_app():
    """使用Hypercorn启动Flask应用"""
    try:
        hyper_config = HyperConfig()
        hyper_config.bind = ["127.0.0.1:5000"]
        hyper_config.use_reloader = True
        hyper_config.workers = 1
        hyper_config.access_log_format = '%(h)s %(r)s %(s)s %(b)s %(D)s'
        
        logger.info("Starting Flask application on port 5000")
        await serve(app, hyper_config)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}")
        raise

async def main():
    """主函数：同时启动Flask和WebSocket服务器"""
    try:
        # 创建任务列表
        tasks = [
            asyncio.create_task(start_flask_app()),
            asyncio.create_task(start_websocket_server())
        ]
        
        # 等待所有任务完成
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # 在Windows平台上需要使用SelectEventLoop
        if asyncio.get_event_loop().is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
        
        # 获取或创建事件循环
        loop = asyncio.get_event_loop()
        
        # 运行主函数
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Application shutdown requested")
    except Exception as e:
        logger.error(f"Application crashed: {str(e)}")
    finally:
        # 清理和关闭事件循环
        try:
            loop.close()
        except:
            pass
        logger.info("Application shutdown complete")

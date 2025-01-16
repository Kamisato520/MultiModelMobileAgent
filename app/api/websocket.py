import asyncio
from aiohttp import web
from app.services.websocket_service import WebSocketService

# 创建WebSocket服务实例
websocket_service = WebSocketService()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    try:
        await websocket_service.handle_connection(ws, request.path)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        return ws

def setup_websocket(app):
    app.route.add_get('/ws', websocket_handler) 
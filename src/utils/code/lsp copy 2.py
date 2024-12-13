import asyncio
from anyio import Path
import websockets
import json
import uuid

async def connect_to_lsp():
    uri = "ws://localhost:2087"  # 假设 WebSocket 服务运行在本地的 2087 端口
    file_path = Path("D:/github/codebiu/server-example/src/utils/code/ast_all.py")
    rootUri = file_path.as_uri()  # 这会自动生成正确的URI格式
    position = {'line': 274, 'character': 44}  # 指定函数的行号和列号（示例位置）
    async with websockets.connect(uri) as websocket:
        # 创建一个初始化消息
        message = {
            'jsonrpc': '2.0',
            'id': str(uuid.uuid4()),  # 使用 UUID 生成唯一的请求 ID
            'method': 'initialize',  # LSP 初始化方法
            'params': {
                'processId': None,
                'rootUri': rootUri,
                'capabilities': {}
            }
        }

        # 发送初始化请求
        await websocket.send(json.dumps(message))

        # 等待响应
        response = await websocket.recv()
        print(f"Received: {response}")

# 运行事件循环
asyncio.run(connect_to_lsp())


import asyncio
import json
import uuid
import websockets
from anyio import Path
# pip install python-lsp-server
# pylsp --ws -v
async def connect_to_lsp():
    uri = "ws://localhost:2087"  # 假设 WebSocket 服务运行在本地的 2087 端口
    file_path = Path(r"D:\github\codebiu\server-example\src")
    rootUri = file_path.as_uri()  # 生成文件的 URI 格式
    use_file_path = Path(r"D:\github\codebiu\server-example\src\utils\rag\graph_rag.py")
    use_Uri = use_file_path.as_uri()  # 生成文件的 URI 格式
    position = {'line': 273, 'character': 44}  # 指定函数的行号和列号（示例位置）
    # position = {'line': 21, 'character': 30}  # 指定函数的行号和列号（示例位置）


    # file_path = Path(r"D:\github\codebiu\server-example\src\utils\rag\graph_rag.py")
    # rootUri = file_path.as_uri()  # 生成文件的 URI 格式
    # position = {'line': 274, 'character': 44}  # 指定函数的行号和列号（示例位置）
    async with websockets.connect(uri) as websocket:
        # 创建初始化消息
        message = {
            'jsonrpc': '2.0',
            'id': str(uuid.uuid4()),  # 使用 UUID 生成唯一的请求 ID
            'method': 'initialize',  # LSP 初始化方法
            'params': {
                'processId': None,
                'rootUri': rootUri,
                'workspaceFolders': rootUri,#?????????????????????????
                'capabilities': {}
            }
        }

        # 发送初始化请求
        await websocket.send(json.dumps(message))
        
        # 等待初始化响应
        response = await websocket.recv()
        # print(f"Received Initialization Response: {response}")

        # 获取函数定义位置
        definition_message = {
            'jsonrpc': '2.0',
            'id': str(uuid.uuid4()),  # 新的请求 ID
            'method': 'textDocument/definition',
            'params': {
                'textDocument': {'uri': use_Uri},
                'position': position
            }
        }

        # 发送请求获取定义位置
        await websocket.send(json.dumps(definition_message))
        definition_response = await websocket.recv()
        print(f"Function Definition: {definition_response}")
        
        
        
        # 获取函数引用位置
        references_message = {
            'jsonrpc': '2.0',
            'id': str(uuid.uuid4()),  # 新的请求 ID
            'method': 'textDocument/references',
            'params': {
                'textDocument': {'uri': use_Uri},
                'position': position,
                'context': {'includeDeclaration': True}
            }
        }

        # 发送请求获取引用位置
        await websocket.send(json.dumps(references_message))
        references_response = await websocket.recv()
        print(f"Function References: {references_response}")
        
        
        
         # 获取当前位置的符号信息（如符号名称、类型、文档等）
        hover_message = {
            'jsonrpc': '2.0',
            'id': str(uuid.uuid4()),  # 新的请求 ID
            'method': 'textDocument/hover',
            'params': {
                'textDocument': {'uri': use_Uri},
                'position': position
            }
        }

        # 发送请求获取符号信息
        await websocket.send(json.dumps(hover_message))
        hover_response = await websocket.recv()
        print(f"Hover Information: {hover_response}")

# 运行事件循环
asyncio.run(connect_to_lsp())

import json
import asyncio
import websockets
from pathlib import Path

class LSPClient:
    def __init__(self, server_host='localhost', server_port=2087):
        # 初始化LSP客户端，设置服务器的主机和端口
        self.server_host = server_host
        self.server_port = server_port
        self.websocket = None  # 将 client_socket 改为 websocket

    async def start_server(self):
        """启动LSP服务器并与其建立连接（WebSocket）。"""
        uri = f"ws://{self.server_host}:{self.server_port}"  # WebSocket的连接URI
        try:
            # 通过websockets连接到LSP服务器
            self.websocket = await websockets.connect(uri)
            print(f"Connected to LSP server at {uri}")
            # 启动监听循环，等待响应
            await self._listen()
        except (ConnectionRefusedError, ConnectionAbortedError) as e:
            print(f"连接失败: {e}")
            # 这里可以加入重试机制或退出程序
        except Exception as e:
            print(f"其他错误: {e}")

    async def _listen(self):
        """监听来自WebSocket服务器的消息。"""
        while True:
            try:
                message = await self.websocket.recv()  # 从WebSocket接收消息
                if message:
                    print(f"Received message: {message.strip()}")  # 打印接收到的消息
                    await self._handle_message(message)  # 处理接收到的消息
                else:
                    break  # 如果没有消息，则跳出循环
            except Exception as e:
                print(f"Error listening: {e}")
                break

    async def _handle_message(self, message):
        """处理接收到的LSP消息。"""
        try:
            data = json.loads(message)  # 将消息解析为JSON格式
            if 'method' in data:
                # 根据不同的method字段，调用对应的处理方法
                if data['method'] == 'textDocument/definition':
                    await self._handle_definition(data)  # 处理函数定义响应
                elif data['method'] == 'textDocument/references':
                    await self._handle_references(data)  # 处理函数引用响应
                elif data['method'] == 'textDocument/hover':
                    await self._handle_hover(data)  # 处理悬停信息响应
        except json.JSONDecodeError:
            pass  # 如果消息格式无效，跳过

    async def _handle_definition(self, data):
        """处理函数定义的响应。"""
        definition = data.get('result', None)  # 获取函数定义的位置信息
        if definition:
            print(f"Function definition found at {definition['uri']}:{definition['range']['start']}")
        else:
            print("No definition found.")  # 如果没有找到定义，输出提示信息

    async def _handle_references(self, data):
        """处理函数引用（调用）的响应。"""
        references = data.get('result', [])  # 获取所有函数引用的位置信息
        if references:
            for ref in references:
                print(f"Function call found at {ref['uri']}:{ref['range']['start']}")
        else:
            print("No references found.")  # 如果没有找到引用，输出提示信息

    async def _handle_hover(self, data):
        """处理函数的悬停信息（例如函数签名、类型、注释等）。"""
        hover_info = data.get('result', None)  # 获取悬停信息
        if hover_info:
            print(f"Hover information: {hover_info['contents']}")
        else:
            print("No hover information available.")  # 如果没有悬停信息，输出提示信息

    async def request_function_definition(self, uri, position):
        """请求LSP服务器返回指定位置的函数定义。"""
        request = {
            'jsonrpc': '2.0',
            'method': 'textDocument/definition',
            'params': {
                'textDocument': {'uri': uri},  # 文件的URI
                'position': position  # 函数的位置（行号和列号）
            },
            'id': 1  # 请求的ID，用于匹配响应
        }
        await self.websocket.send(json.dumps(request))  # 通过WebSocket发送请求到LSP服务器
        print(f"Sent request for definition at {uri}:{position}")

    async def request_function_references(self, uri, position):
        """请求LSP服务器返回指定位置的函数引用（调用）。"""
        request = {
            'jsonrpc': '2.0',
            'method': 'textDocument/references',
            'params': {
                'textDocument': {'uri': uri},  # 文件的URI
                'position': position  # 函数的位置（行号和列号）
            },
            'id': 2  # 请求的ID，用于匹配响应
        }
        await self.websocket.send(json.dumps(request))  # 通过WebSocket发送请求到LSP服务器
        print(f"Sent request for references at {uri}:{position}")

    async def request_function_hover(self, uri, position):
        """请求LSP服务器返回指定位置的函数悬停信息。"""
        request = {
            'jsonrpc': '2.0',
            'method': 'textDocument/hover',
            'params': {
                'textDocument': {'uri': uri},  # 文件的URI
                'position': position  # 函数的位置（行号和列号）
            },
            'id': 3  # 请求的ID，用于匹配响应
        }
        await self.websocket.send(json.dumps(request))  # 通过WebSocket发送请求到LSP服务器
        print(f"Sent request for hover info at {uri}:{position}")


# 示例用法
def get_file_uri(file_path):
    """将本地文件路径转换为URI格式。"""
    return f'file://{file_path}'


if __name__ == '__main__':
    client = LSPClient()  # 创建LSP客户端实例

    # 启动LSP客户端与LSP服务器连接
    asyncio.run(client.start_server())

    # 示例：传递文件URI和函数位置，查询函数的定义、引用和悬停信息
    file_path = Path("D:/github/codebiu/server-example/src/utils/code/ast_all.py")
    uri = file_path.as_uri()  # 这会自动生成正确的URI格式
    position = {'line': 23, 'character': 26}  # 指定函数的行号和列号（示例位置）

    # 请求函数定义
    asyncio.run(client.request_function_definition(uri, position))

    # 请求函数引用（调用）
    asyncio.run(client.request_function_references(uri, position))

    # 请求函数悬停信息（例如函数签名、类型注释等）
    asyncio.run(client.request_function_hover(uri, position))

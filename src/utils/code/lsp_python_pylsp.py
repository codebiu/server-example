import asyncio
import json
import uuid
import websockets
from anyio import Path

# pip install python-lsp-server
# pylsp --ws -v
import json
from pathlib import Path
import subprocess
from typing import Dict

file_path = Path(r"D:\github\codebiu\server-example\src")
rootUri = file_path.as_uri()  # 生成文件的 URI 格式
use_file_path = Path(r"D:\github\codebiu\server-example\src\utils\rag\graph_rag.py")
use_Uri = use_file_path.as_uri()  # 生成文件的 URI 格式
position = {"line": 273, "character": 44}  # 指定函数的行号和列号（示例位置）


class LspPythonPyright:
    uri = "ws://localhost:2087"

    async def lsp_start(self):
        # # 启动 pyright-langserver
        # self.process = subprocess.Popen(
        #     [r"D:\a_code_lib\conda_env\pc_py\python.exe","-m","pylsp", "--ws", "-v"],
        #     stdin=subprocess.PIPE,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     text=True,
        # )
        # stdout, stderr = self.process.communicate()
        # # 输出 self.process
        # print(stdout)
        self.websocket = await websockets.connect(self.uri,close_timeout=5)

    async def send_request(self, method: str, params: Dict, uuid):
        """发送 JSON-RPC 请求到语言服务器"""
        request = {"jsonrpc": "2.0", "id": uuid, "method": method, "params": params}
        # message = json.dumps(request) + "\n"
        message = json.dumps(request)
        # 发送初始化请求
        await self.websocket.send(message)

    async def receive_response(self):
        """接收语言服务器的响应"""
        definition_response = await self.websocket.recv()
        # response = json.loads(stdout)
        return definition_response


if __name__ == "__main__":
    import uuid

    async def connect_to_lsp():
        lspPythonPyright = LspPythonPyright()
        await lspPythonPyright.lsp_start()

        # rootUri = Path(
        #     r"D:\github\codebiu\server-example\src"
        # ).as_uri()  # 生成文件的 URI 格式
        # use_Uri = Path(
        #     r"D:\github\codebiu\server-example\src\utils\rag\graph_rag.py"
        # ).as_uri()
        # position = {"line": 273, "character": 44}  # 指定函数的行号和列号（示例位置）

        # # 初始化请求
        # initialize_params = {
        #     "processId": None,
        #     "rootUri": rootUri,
        #     "capabilities": {},
        # }
        # await lspPythonPyright.send_request(
        #     "initialize", initialize_params, str(uuid.uuid4())
        # )
        # response = await lspPythonPyright.receive_response()
        # print("Initialize Response:", response)

        # # 查找函数定义
        # definition_params = {
        #     "textDocument": {"uri": use_Uri},
        #     "position": position,
        # }
        # await lspPythonPyright.send_request(
        #     "textDocument/definition", definition_params, str(uuid.uuid4())
        # )
        # response = await lspPythonPyright.receive_response()
        # print("Definition Response:", response)


# 运行事件循环
asyncio.run(connect_to_lsp())

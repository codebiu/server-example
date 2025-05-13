import asyncio, json, subprocess, uuid
from pathlib import Path

class LspPythonPyright:

    async def lsp_start(self):
        # 启动 pyright-langserver
        self.process = await asyncio.create_subprocess_exec(
            # ["pyright-langserver", "--stdio"],
            "D:/a_code_lib/conda_env/pc_py/Scripts/pyright-langserver.exe", "--stdio",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # 监听来自语言服务器的标准输出。
        asyncio.create_task(self.receive_response())
        asyncio.create_task(self.receive_error())

    async def send_request(self, method: str, params: dict, uuid = None):
        """发送 JSON-RPC 请求到语言服务器 头部总是 ASCII 编码，而消息体总是 UTF-8 编码！"""
        json_data = {"jsonrpc": "2.0", "method": method, "params": params}
        if uuid: json_data["id"] = uuid
        utf8_encoded_body = json.dumps(json_data).encode("utf-8")
        # 消息头
        header = f"Content-Length: {len(utf8_encoded_body)}\r\nContent-Type: application/vscode-jsonrpc; charset=utf-8\r\n\r\n"
        ascii_encoded_header = header.encode("ascii")
         # 头部总是 ASCII 编码，而消息体总是 UTF-8 编码！
        self.process.stdin.write(ascii_encoded_header)
        self.process.stdin.write(utf8_encoded_body)
        await self.process.stdin.drain()

    async def receive_response(self):
        """接收语言服务器的响应"""
        while True:
            line = await self.process.stdout.readline()
            if not line:
                break
            result = line.decode("utf-8")
            print(f"返回信息: {result}")
            
    async def receive_error(self):
        """接收语言服务器的响应"""
        while True:
            line = await self.process.stderr.readline()
            if line:
                result = line.decode("utf-8")
                print(f"返回error信息: {result}")
            

    async def shutdown_and_exit(self):
        """发送 shutdown 和 exit 请求以关闭语言服务器"""
        # 发送 shutdown 请求
        await self.send_request("shutdown", {}, str(uuid.uuid4()))
        
        # # 发送 exit 请求
        # await self.send_request("exit", {}, str(uuid.uuid4()))

        # 确保语言服务器退出
        # await self.process.wait()


if __name__ == "__main__":
    import uuid
    rootUri = Path(r"D:\github\codebiu\server-example\src").as_uri()  # 生成文件的 URI 格式
    use_Uri = Path(r"D:\github\codebiu\server-example\src\utils\rag\graph_rag.py").as_uri()
    position = {'line': 273, 'character': 44}  # 指定函数的行号和列号（示例位置）
    # 主程序入口
    async def main():

        lsp = LspPythonPyright()
        await lsp.lsp_start()    
         # 初始化请求
        initialize_params = {
            "processId": None,
            # "rootPath": rootUri,
            # 'workspaceFolders': rootUri,
            "workspaceFolders": [{"uri": rootUri, "name": "utils"}] , # 提供工作空间文件夹
            "capabilities": {},
        }
        await lsp.send_request("initialize", initialize_params,str(uuid.uuid4()))
        # # # 发送初始化通知。
        await lsp.send_request("initialized", {})
       
        # 查找函数定义
        definition_params = {
            "textDocument":  {'uri': use_Uri},
            "position": position,
        }
        await lsp.send_request("textDocument/definition", definition_params,str(uuid.uuid4()))
        # 关闭
        await lsp.shutdown_and_exit()
        # 关闭进程
        await lsp.process.wait()
    asyncio.run(main())

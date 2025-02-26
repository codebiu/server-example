import asyncio, json, subprocess, uuid
import time
from pathlib import Path
from typing import Union, Any
from abc import ABC, abstractmethod

import aiofiles

# type
StringDict = dict[str, Any]

class Lsp(ABC):
    def __init__(self, logger=print):
        # json编码
        self.HEAD_ENCODING = "utf-8"
        self.ENCODING = "utf-8"
        # 
        self.logger = logger
        # 异步事件
        self.tasks = []
        # 请求中 完成后pop
        self._response_handlers: dict[str, asyncio.Future] = {}
        # 接收
        self._receive_info_out = {}
        self._receive_info_err = {}
        

    async def start(self, process_list: list, root_path: Path) -> None:
        """
        启动语言服务器进程，并创建任务以持续从其stdout stderr读取，以处理来自服务器的客户端通信
        """
        self.process = await asyncio.create_subprocess_exec(
            *process_list,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # 启动接收响应的任务
        self.tasks.append(asyncio.create_task(self.loop_stdout()))
        self.tasks.append(asyncio.create_task(self.loop_stderr()))
        # 初始化语言服务器
        self.rootUri = root_path.as_uri()
        await self._initialize()
        
    async def references(self, use_path: Path, line: int, character: int):
        use_uri = use_path.as_uri()
        message = {
            "textDocument": {"uri": use_uri},
            "position": {"line": line, "character": character},
            "context": {
                # 不包含定义位置
                "includeDeclaration": False,
            },
        }
        return await self._send("textDocument/references", message)
        
    async def _open_file(self, use_path: Path):
        use_uri = use_path.as_uri()
        async with aiofiles.open(use_path, mode='r', encoding='utf-8') as f:
            contents = await f.read()
            message = {
                "textDocument": {"uri": use_uri, 'text': contents},
            }
            await self._send("textDocument/didOpen", message)

    async def _initialize(self):
        """初始化语言服务器"""
        initialize_params = {
            "processId": None,
            "rootUri": self.rootUri,
            "workspaceFolders": [
                {"uri": self.rootUri, "name": "utils"}
            ],  # 提供工作空间文件夹
            "capabilities": {},
        }
        await self._send("initialize", initialize_params, str(uuid.uuid4()))
        await self._send_no_id("initialized", {})

    async def _send(self, method: str, params: dict, request_id=None) -> asyncio.Future:
        """发送 JSON-RPC 请求到语言服务器 写入stdio"""
        if request_id is None:
            request_id = str(uuid.uuid4())  # 如果没有指定请求 ID，则生成一个新的 UUID
        if not self.process or not self.process.stdin:
            raise RuntimeError("Process or stdin is not available")
        
        request_future = asyncio.get_running_loop().create_future()
        self._response_handlers[request_id] = request_future
        
        # 构造 JSON-RPC 请求的内容
        msg_body = Lsp._make_request(method, request_id, params)
        msg = self._create_message(msg_body)
        # if self.logger:
        #     self.logger("send_:", msg)
        self.process.stdin.write(b''.join(msg))
        await self.process.stdin.drain()
        # 返回 Future 对象 在异步输出中设置
        result = await request_future  
        return result
    
    async def _send_no_id(self, method: str, params: dict) -> asyncio.Future:
        """发送 JSON-RPC 请求到语言服务器 写入stdio"""
        # 构造 JSON-RPC 请求的内容
        msg_body = Lsp._make_request_no_id(method, params)
        msg = self._create_message(msg_body)
        # if self.logger:
        #     self.logger("send_:", msg)
        self.process.stdin.write(b''.join(msg))
        await self.process.stdin.drain()
    
    
        
    async def stop(self):
        """停止语言服务器"""
        # 取消所有任务并等待它们完成
        for task in self.tasks:
            task.cancel()
        # 清空任务列表
        self.tasks.clear()
        # 终止和清理进程
        if self.process:
            # 关闭标准输入、输出和错误流
            if self.process.stdin:
                self.process.stdin.close()
            try:
                self.process.terminate()  # 尝试正常终止进程
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=1)  # 等待进程结束，最多等待2秒
                except asyncio.TimeoutError:
                    self.process.kill()  # 如果进程没有在规定时间内结束，则强制杀死
                await self.process.wait()  # 确保进程已被杀死
            except ProcessLookupError:
                pass  # 进程可能已经结束了
            finally:
                self.process = None
        print('停止语言服务器')
    # 辅助请求函数
    @staticmethod
    def _make_response(request_id, params) -> StringDict:
        return {"jsonrpc": "2.0", "id": request_id, "result": params}

    @staticmethod
    def _make_request(method: str, request_id, params) -> StringDict:
        return {"jsonrpc": "2.0", "method": method, "id": request_id, "params": params}
    @staticmethod
    def _make_request_no_id(method: str, params) -> StringDict:
        return {"jsonrpc": "2.0", "method": method, "params": params}

    def _create_message(self, body_dict) -> tuple[bytes, bytes, bytes]:
        '''构造JSON-RPC内容'''
        # HEAD_ENCODING 可以是 "ascii"
        body = json.dumps(
            body_dict, check_circular=False, ensure_ascii=False, separators=(",", ":")
        ).encode(self.ENCODING)
        return (
            f"Content-Length: {len(body)}\r\n".encode(self.HEAD_ENCODING),
            "Content-Type: application/vscode-jsonrpc; charset=utf-8\r\n\r\n".encode(
                self.ENCODING
            ),
            body,
        )

    # 接收
    async def loop_stdout(self) -> None:
        """
        读取来自语言服务器进程stdout的消息，并调用已注册的响应和通知处理程序
        """
        try:
            while (
                self.process
                and self.process.stdout
                and not self.process.stdout.at_eof()
            ):
                line = await self.process.stdout.readline()
                if not line:
                    continue
                # if self.logger:
                #     self.logger("stdout_:", line)
                try:
                    num_bytes = self._content_length(line)
                except ValueError:
                    continue
                if num_bytes is None:
                    continue
                # 是换行就向下读取
                while line and line.strip():
                    line = await self.process.stdout.readline()
                if not line:
                    continue
                body_json = await self.process.stdout.readexactly(num_bytes)
                # if self.logger:
                #     self.logger("body:", body_json)
                body_dict = json.loads(body_json)
                id = body_dict.get("id")
                if id and id in self._response_handlers:
                    future = self._response_handlers.pop(id)
                    future.set_result(body_dict)  # 设置 Future 的结果
        except (BrokenPipeError, ConnectionResetError):
            if self.logger:
                self.logger("Language server process has terminated.")
            pass

    async def loop_stderr(self) -> None:
        """
        读取stderr
        """
        while self.process and self.process.stderr and not self.process.stderr.at_eof():
            line = await self.process.stderr.readline()
            if not line:
                continue
            if self.logger:
                self.logger("stderr_:", line)

    @staticmethod
    def _content_length(line: bytes) -> int:
        if line.startswith(b"Content-Length: "):
            _, value = line.split(b"Content-Length: ")
            value = value.strip()
            try:
                return int(value)
            except ValueError:
                raise ValueError("Invalid Content-Length header: {}".format(value))

# 主程序入口
if __name__ == "__main__":
    root_path = Path(
        "D:/project/dhc2024/LLM/llm_ai4se_code_analysis_assistant_backend/temp/5e579f66-9fb0-42f0-a882-5dc61c635481"
    )
    use_path = Path(
        "D:/project/dhc2024/LLM/llm_ai4se_code_analysis_assistant_backend/temp/5e579f66-9fb0-42f0-a882-5dc61c635481/app/controllers/address_books_controller.rb"
    )
    positions = [
        {"line": 150, "character": 7}
    ]

    async def main():
        lsp = Lsp()
        # 启动并初始化语言服务器
        await lsp.start(["D:\\a_code_lib\\Ruby33-x64\\bin\\solargraph.bat", "stdio"], root_path)
        # 等待5s
        await asyncio.sleep(1)
        
        # 发送请求
        for position in positions:
            await lsp._open_file(use_path)
            response = await lsp.references(use_path, position["line"], position["character"])
            # response = await response_future
            print("Response:", response)
        
        await lsp.stop()
        # # 等待语言服务器进程结束
        # await lsp.process.wait()
        print('end')

    asyncio.run(main())
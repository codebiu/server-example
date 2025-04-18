import asyncio
import json
import uuid
from pathlib import Path
from typing import  Any
from abc import ABC

# type
StringDict = dict[str, Any]


class PyShell(ABC):
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

    async def start(self, process_list: list) -> None:
        """
        启动服务器shell进程，并创建任务以持续从其stdout stderr读取，以处理来自服务器的客户端通信
        """
        self.process = await asyncio.create_subprocess_shell(
            *process_list,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # 启动接收响应的任务
        self.tasks.append(asyncio.create_task(self.loop_stdout()))
        self.tasks.append(asyncio.create_task(self.loop_stderr()))


    async def _send(self, msg, request_id=None) -> asyncio.Future:
        """发送服务器 写入stdio"""
        if request_id is None:
            request_id = str(uuid.uuid4())  # 如果没有指定请求 ID，则生成一个新的 UUID
        if not self.process or not self.process.stdin:
            raise RuntimeError("Process or stdin is not available")
        request_future = asyncio.get_running_loop().create_future()
        self._response_handlers[request_id] = request_future
        self.process.stdin.write(msg)
        await self.process.stdin.drain()
        # 返回 Future 对象 在异步输出中设置
        result = await request_future
        return result



    async def stop(self):
        """停止shell服务器"""
        await self._send_no_id("shutdown", {})
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
                    await asyncio.wait_for(
                        self.process.wait(), timeout=1
                    )  # 等待进程结束，最多等待2秒
                except asyncio.TimeoutError:
                    self.process.kill()  # 如果进程没有在规定时间内结束，则强制杀死
                await self.process.wait()  # 确保进程已被杀死
            except ProcessLookupError:
                pass  # 进程可能已经结束了
            finally:
                self.process = None
        print("停止shell服务器")


    # 接收
    async def loop_stdout(self) -> None:
        """
        读取来自shell服务器进程stdout的消息，并调用已注册的响应和通知处理程序
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
                
                print(body_json)
                
                # if self.logger:
                #     self.logger("body!!:", body_json)
                body_dict = json.loads(body_json)
                id = body_dict.get("id")
                if id and id in self._response_handlers:
                    future = self._response_handlers.pop(id)
                    future.set_result(body_dict)  # 设置 Future 的结果
        except (BrokenPipeError, ConnectionResetError):
            if self.logger:
                self.logger("shell server process has terminated.")
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
    async def main():
        pyShell = PyShell()
 

    asyncio.run(main())

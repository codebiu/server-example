import asyncio
import sys
from pathlib import Path

class InteractiveShell:
    def __init__(self):
        self.process = None
        self.running = False

    async def start(self):
        """启动跨平台shell会话"""
        if sys.platform == "win32":
            # Windows: 启动PowerShell进程
            self.process = await asyncio.create_subprocess_exec(
                "powershell.exe",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        else:
            # Unix/Linux/Mac: 启动bash进程
            self.process = await asyncio.create_subprocess_exec(
                "/bin/bash",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        self.running = True
        # 启动输出监控任务
        self.output_task = asyncio.create_task(self._monitor_output())

    async def _monitor_output(self):
        """监控进程输出"""
        while self.running and self.process and self.process.stdout:
            line = await self.process.stdout.readline()
            if not line:
                break
            output = line.decode().strip()
            print(f"{output}")

    async def execute(self, command: str):
        """执行命令"""
        if not self.running or not self.process or not self.process.stdin:
            raise RuntimeError("Shell session is not running")
        
        # 发送命令并换行
        self.process.stdin.write(f"{command}\n".encode())
        await self.process.stdin.drain()

    async def stop(self):
        """停止会话"""
        if self.running:
            self.running = False
            if self.process:
                try:
                    # 发送退出命令
                    if self.process.stdin:
                        self.process.stdin.write(b"exit\n")
                        await self.process.stdin.drain()
                    
                    # 等待进程结束
                    await asyncio.wait_for(self.process.wait(), timeout=2)
                except (asyncio.TimeoutError, ProcessLookupError):
                    if self.process:
                        self.process.kill()
                        await self.process.wait()
                finally:
                    self.process = None
            
            # 取消输出监控任务
            if self.output_task and not self.output_task.done():
                self.output_task.cancel()
                try:
                    await self.output_task
                except asyncio.CancelledError:
                    pass

async def read_input(prompt: str = "> ") -> str:
    """异步读取用户输入"""
    return await asyncio.get_event_loop().run_in_executor(None, input, prompt)



if __name__ == "__main__":
    async def main():
        shell = InteractiveShell()
        try:
            await shell.start()
            
            while shell.running:
                try:
                    # 读取用户输入
                    command = await read_input(">")
                    
                    if command == ":q":
                        print("正在结束会话...")
                        await shell.stop()
                        break
                    
                    # 执行命令pwd
                    await shell.execute(command)
                    
                except KeyboardInterrupt:
                    print("\n检测到Ctrl+C，正在结束会话...")
                    await shell.stop()
                    break
                    
        except Exception as e:
            print(f"错误: {str(e)}")
        finally:
            if shell.running:
                await shell.stop()
    asyncio.run(main())
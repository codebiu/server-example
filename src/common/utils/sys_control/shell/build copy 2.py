import asyncio
import sys

async def execute_pwd(command):
    """跨平台执行pwd/cd命令"""
    if sys.platform == "win32":
        # Windows: 通过PowerShell执行pwd
        """使用 PowerShell 执行命令"""
        process = await asyncio.create_subprocess_exec(
            "powershell.exe", command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    else:
        # Unix/Linux/Mac
        process = await asyncio.create_subprocess_exec(
            # /bin/bash -c "ls"
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode == 0:
        return stdout.decode().strip()
    else:
        raise RuntimeError(f"Failed to get directory: {stderr.decode().strip()}")
if __name__ == "__main__":
    async def main():
        try:
            # 方法1：使用子进程
            # dir1 = await execute_pwd("pwd")
            dir1 = await execute_pwd("conda env list")
            print(f"Command output: {dir1}")
        except Exception as e:
            print(f"Error: {str(e)}")

    asyncio.run(main())
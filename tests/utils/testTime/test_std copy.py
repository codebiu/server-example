import asyncio

async def run_script():
    # 启动子进程，执行指定的脚本文件
    process = await asyncio.create_subprocess_exec(
        'python', r"D:\github\codebiu\server-example\tests\utils\testTime\test.py", # 替换成你实际的脚本路径
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE
    )
    
    # 定期发送 'hello' 消息到脚本的输入流
    async def send_hello():
        while True:
            await asyncio.sleep(3)
            process.stdin.write(b'hello\n')
            await process.stdin.drain()
    
    # 创建一个任务发送 'hello' 消息
    asyncio.create_task(send_hello())
    
    # 读取脚本输出
    async def read_output():
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            print(f"子进程输出: {line.decode().strip()}")
    
    # 创建任务读取子进程的标准输出
    asyncio.create_task(read_output())
    
    # 等待子进程完成
    await process.wait()

# 运行 asyncio 事件循环
asyncio.run(run_script())

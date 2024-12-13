import asyncio
import websockets
import subprocess

async def lsp_handler(websocket, path):
    # 启动 Pyright 语言服务器，使用 --stdio 模式
    pyright_process = subprocess.Popen(
        ['pyright-langserver', '--stdio'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # 从 WebSocket 接收消息并发送给 Pyright
    async for message in websocket:
        pyright_process.stdin.write(message.encode('utf-8'))
        pyright_process.stdin.flush()

        # 从 Pyright 读取响应并通过 WebSocket 发送给客户端
        output = pyright_process.stdout.readline()
        while output:
            await websocket.send(output.decode('utf-8'))
            output = pyright_process.stdout.readline()

    # 处理关闭事件
    pyright_process.stdin.close()
    pyright_process.stdout.close()
    pyright_process.stderr.close()
    pyright_process.wait()

# 启动 WebSocket 服务器
async def start_server():
    server = await websockets.serve(lsp_handler, 'localhost', 2087)
    print("WebSocket server running on ws://localhost:2087")
    await server.wait_closed()

# 启动事件循环
asyncio.run(start_server())

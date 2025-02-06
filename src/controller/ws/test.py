import json
from fastapi import WebSocket,APIRouter
from config.fastapi_config import app
import aiofiles

from fastapi.responses import HTMLResponse

from config.log import console
router = APIRouter()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>	
            let url = window.location.href; /* 获取完整URL */
            url = url.replace("http", "ws");
            url = url + "test";
            alert(url); 
            var ws = new WebSocket(url);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get("/")
async def get():
    return HTMLResponse(html)


@router.websocket("/test")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
        
        
        
# 定义 WebSocket 路由
@router.websocket("/camera")
async def websocket_endpoint(websocket: WebSocket):
    # 接受 WebSocket 连接
    await websocket.accept()
    try:
        # 打开文件以保存数据
        async with aiofiles.open('test.mp4', "ab") as output_file:
            # 当有数据到达时
            while True:
                # 接收数据
                data = await websocket.receive_bytes()
                
                # 将数据写入文件
                await output_file.write(data)
                console.log('输出数据到文件中...')
                
    except Exception as e:
        print("WebSocket connection error:", str(e))
        
        
# 定义 WebSocket 路由
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 接受 WebSocket 连接
    await websocket.accept()
    
    try:
        # 当有数据到达时
        while True:
            # 接收数据
            data = await websocket.receive_text()
            
            # 解析数据
            protocol = json.loads(data)
            
            # 处理解析后的数据
            handle_protocol(protocol)
    
    except Exception as e:
        print("WebSocket connection error:", str(e))

# 处理数据函数
def handle_protocol(protocol: dict):
    # 根据协议类型执行不同的操作
    if 'blob' in protocol:
        # 处理 Blob 数据
        print("Received Blob:", protocol['blob'])
    if 'json' in protocol:
        # 处理 JSON 数据
        print("Received JSON:", protocol['json'])
        
app.include_router(router,prefix="/ws",tags=['ws'])


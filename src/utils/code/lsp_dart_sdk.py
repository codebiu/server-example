import asyncio, json, subprocess, uuid
import time
from pathlib import Path


class LspDarkSDK:
    def __init__(self):
        self.message_get = {}  # 存储收到的消息
        self.pending_requests = set()  # 跟踪未完成的请求 ID
        self.buffer = bytearray()
        self.header_content_length = None
       
    def check_end(self,length):
        """设置结束条件"""
        self.tasks_end_len = length
        # 每次请求超时秒数
        self.time_start = time.time()
        self.over_time =20
        # 已处理
        self.tasks_end_len_over = 0
         # 启动完成检查的任务
        self.check_end_listener_task = asyncio.create_task(self.check_end_task())   
    
    async def check_end_task(self):
        """完成或超时结束"""
        while True:  # 当 stop_event 没有被触发时持续接收
            await asyncio.sleep(1)
            # 有新数据
            if self.message_get.__len__() != self.tasks_end_len_over:
                self.time_start = time.time()
                self.tasks_end_len_over = self.message_get.__len__()
                if not self.pending_requests and self.tasks_end_len_over == self.tasks_end_len:
                    print("请求已完成.....") 
                    await self.end()
            if time.time() - self.time_start > self.over_time :
                print(f"请求超时..总请求数:{self.tasks_end_len}...已处理数:{self.tasks_end_len_over}") 
                await self.end()
                return
               

    async def lsp_start(self):
        """启动 Dart 语言服务器"""
        # 使用 subprocess 启动 Dart 语言服务器，并设置 stdin 和 stdout 进行通信
        self.process = await asyncio.create_subprocess_exec(
            "dart",
            "language-server",
            "--diagnostic-port=8100",  # 设置诊断端口
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE
        )
        # 启动接收响应的任务
        self.response_listener_task = asyncio.create_task(self.receive_response())

    async def initialize(self, rootUri):
        """初始化语言服务器"""
        self.pending_requests = set()
        initialize_params = {
            "processId": None,
            "rootUri": rootUri,
            "capabilities": {},  # 语言服务器的能力，可以根据需要扩展
        }
        await self.send_request("initialize", initialize_params, str(uuid.uuid4()))
        await self.send_request("initialized", {})

    async def send_request(self, method: str, params: dict, request_id=None):
        """发送 JSON-RPC 请求到语言服务器"""
        if request_id is None:
            request_id = str(uuid.uuid4())  # 如果没有指定请求 ID，则生成一个新的 UUID
        # 构造 JSON-RPC 请求的内容
        json_data = {
            "jsonrpc": "2.0",
            "method": method,  # 方法名
            "params": params,  # 请求参数
            "id": request_id,  # 请求 ID
        }
        # 将 JSON 数据转化为 UTF-8 编码
        utf8_encoded_body = json.dumps(json_data).encode("utf-8")
        # 构造 HTTP 头
        header = f"Content-Length: {len(utf8_encoded_body)}\r\nContent-Type: application/vscode-jsonrpc; charset=utf-8\r\n\r\n"
        ascii_encoded_header = header.encode("ascii")
        # 向 stdin 写入请求数据
        self.process.stdin.write(ascii_encoded_header)
        self.process.stdin.write(utf8_encoded_body)
        await self.process.stdin.drain()  # 确保数据已经写入
        
    async def send_request_uuid(self, method: str, params: dict, request_id=None):
        """发送 JSON-RPC 记录uuid请求到语言服务器"""
        if request_id is None:
            request_id = str(uuid.uuid4())  # 如果没有指定请求 ID，则生成一个新的 UUID
        self.pending_requests.add(request_id)
        await self.send_request(method, params, request_id)

    async def receive_response(self):
        """接收语言服务器的响应"""
        while True:  # 当 stop_event 没有被触发时持续接收
            # line = await self.process.stdout.readline()  #!! 缓冲区不足
            data = await self.process.stdout.read(1024)  # 假设我们每次读取 1024 字节
            if not data:
                continue  # 如果没有数据，退出循环
            for element in data:
                self.buffer.append(element)
                await self._process_buffer()
               
    async def _process_buffer(self):
        """处理缓冲区中的数据 解析json_rpc响应"""
        L = len(self.buffer)
        if self._ends_with_crlf_crlf(L):
            header_raw = self.buffer.decode("utf-8")
            self.buffer.clear()
            headers = header_raw.split("\r\n")
            # print(f"Headers: {headers}")
            content_length_header = next(
                (header for header in headers if header.startswith("Content-Length:")),
                None,
            )
            if content_length_header:
                self.header_content_length = int(
                    content_length_header[len("Content-Length:") :].strip()
                )

        elif self.header_content_length is not None and L == self.header_content_length:
            # 如果缓冲区的数据量达到了 Content-Length，解析消息体
            message_string = self.buffer[: self.header_content_length].decode( "utf-8" )
            self.buffer.clear()  # 清空缓冲区
            self.header_content_length = None  # 重置内容长度
            # print(f"messageString: {message_string}")              
            extracted_data = self.extract_json_with_id( message_string )  
            if extracted_data is None:  
                return
            response_id = extracted_data.get("id")  # 获取响应的 ID
            if response_id and response_id in self.pending_requests:
                self.message_get[response_id] = extracted_data.get("result")  # 存储响应数据
                self.pending_requests.discard( response_id )  # 移除已完成的请求 ID
                print("返回带id数据...",self.message_get.__len__())

    def extract_json_with_id(self, raw_string):
        """提取带有 ID 的 JSON 数据"""
        try:
            start = raw_string.find("{")
            end = raw_string.rfind("}")
            if start == -1 or end == -1:
                return None
            json_string = raw_string[start : end + 1]
            json_data = json.loads(json_string)  # 将字符串解析为 JSON 对象
            return json_data if "id" in json_data else None  # 仅返回包含 "id" 的数据
        except json.JSONDecodeError:
            return None                
                    
    def _ends_with_crlf_crlf(self, L):
        # 检查缓冲区是否以 CRLF CRLF 结束
        result = (
            L > 4
            and self.buffer[L - 1] == 10
            and self.buffer[L - 2] == 13
            and self.buffer[L - 3] == 10
            and self.buffer[L - 4] == 13
        )
        return result


    async def end(self):
        """发送 shutdown 和 exit 请求以关闭语言服务器"""
        self.check_end_listener_task.cancel()
        self.response_listener_task.cancel()
        print("关闭语言服务器...")
        if self.process:
            # 请求终止进程
            self.process.terminate()
            self.process.kill()
        
        
 
    async def references(self,use_path:str,line:int,character:int):
        """
        发送一个请求以获取给定位置处符号的所有引用。

        参数:
        use_path (str): 符号所在文件的路径
        line (int): 符号所在的行号（从0开始计数）。
        character (int): 符号所在行中的字符位置（从0开始计数）。
        """
        use_Uri = Path(use_path).as_uri()
        references_message = {
            "textDocument": {"uri": use_Uri},
            "position": {"line": line, "character": character},
            "context": {
                # 不包含定义位置
                "includeDeclaration": False,
            },
        }
        
        uuid_this = str(uuid.uuid4())
        await self.send_request_uuid(
            "textDocument/references", references_message, uuid_this
        )
        print("发送请求...")
        return uuid_this



# 主程序入口
if __name__ == "__main__":
    # 设置根目录 URI 和文件 URI
    rootUri = Path("D:/project/test/sdk-3.5.0/pkg/analysis_server").as_uri()
    use_Uri = Path(
        "D:/project/test/sdk-3.5.0/pkg/analysis_server/tool/spec/check_all_test.dart"
    ).as_uri()
    # 定义请求位置列表
    positions = [
        {"line": 18, "character": 31},
        {"line": 18, "character": 31},
        {"line": 18, "character": 31},
    ]

    async def main():
        lsp = LspDarkSDK()

        # 启动并初始化语言服务器
        await lsp.lsp_start()
        await lsp.initialize(rootUri)

        # 发送请求
        for position in positions:
            definition_params = {
                "textDocument": {"uri": use_Uri},
                "position": position,
            }

            await lsp.send_request(
                "textDocument/definition", definition_params, str(uuid.uuid4())
            )

        # 获取函数引用位置
        references_message = {
            "textDocument": {"uri": use_Uri},
            "position": {"line": 18, "character": 31},
            "context": {
                # 不包含定义位置
                "includeDeclaration": False,
            },
        }

        await lsp.send_request(
            "textDocument/references", references_message, str(uuid.uuid4())
        )

        # 关闭语言服务器
        await lsp.end()
        print("所有请求完成，结果:")
        print(json.dumps(lsp.message_get))

        # 启动并初始化语言服务器
        await lsp.lsp_start()
        await lsp.initialize(rootUri)
        # 发送第二个请求批次
        for position in positions:
            definition_params = {
                "textDocument": {"uri": use_Uri},
                "position": position,
            }
            await lsp.send_request(
                "textDocument/definition", definition_params, str(uuid.uuid4())
            )

        # 设置一个新的 stop_event 以等待第二个批次请求完成

        # await lsp.stop_event.wait()
        # 关闭语言服务器
        await lsp.end()
        print("第二个批次请求完成，结果:")
        print(json.dumps(lsp.message_get, indent=1))

    asyncio.run(main())

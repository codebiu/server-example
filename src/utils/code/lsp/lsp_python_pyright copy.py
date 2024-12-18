import asyncio, json, subprocess, uuid
from pathlib import Path


class LspPythonPyright:
    def __init__(self):
        self.message_get = {}  # 存储收到的消息
        self.pending_requests = set()  # 跟踪未完成的请求 ID

    async def lsp_start(self):
        self.stop_event = asyncio.Event()  # 用于停止监听
        """启动 python 语言服务器"""
        # 启动 pyright-langserver
        self.process = await asyncio.create_subprocess_exec(
            # ["pyright-langserver", "--stdio"],
            "D:/a_code_lib/conda_env/pc_py/Scripts/pyright-langserver.exe",
            "--stdio",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    async def initialize(self, rootUri):
        """初始化语言服务器"""
        self.message_get.clear()  # 清空先前存储的消息
        # 启动接收响应的任务
        self.response_listener_task = asyncio.create_task(self.receive_response())
        # 初始化请求参数
        initialize_params = {
            "processId": None,
            # "rootPath": rootUri,
            # 'workspaceFolders': rootUri,
            "workspaceFolders": [{"uri": rootUri, "name": "utils"}] , # 提供工作空间文件夹
            "capabilities": {},
        }
        # 发送初始化请求
        await self.send_request("initialize", initialize_params, str(uuid.uuid4()))
        # 发送初始化完成的信号
        await self.send_request("initialized", {})

    async def send_request(self, method: str, params: dict, uuid=None):
        """发送 JSON-RPC 请求到语言服务器"""
        json_data = {"jsonrpc": "2.0", "method": method, "params": params}
        if uuid:
            json_data["id"] = uuid
            self.pending_requests.add(uuid)  # 记录请求 ID
        # 将 JSON 数据转化为 UTF-8 编码
        utf8_encoded_body = json.dumps(json_data).encode("utf-8")
        # 构造 HTTP 头
        header = f"Content-Length: {len(utf8_encoded_body)}\r\nContent-Type: application/vscode-jsonrpc; charset=utf-8\r\n\r\n"
        ascii_encoded_header = header.encode("ascii")
        # 向 stdin 写入请求数据
        self.process.stdin.write(ascii_encoded_header)
        self.process.stdin.write(utf8_encoded_body)
        await self.process.stdin.drain()  # 确保数据已经写入

    async def receive_response(self):
        """接收语言服务器的响应"""
        while not self.stop_event.is_set():  # 当 stop_event 没有被触发时持续接收
            line = await self.process.stdout.readline()  # 读取语言服务器的输出
            if not line:
                break
            try:
                result = line.decode("utf-8")  # 解码响应数据
                extracted_data = self.extract_json_with_id(
                    result
                )  # 提取有效的 JSON 数据
                if extracted_data:
                    uuid = extracted_data.get("id")  # 获取响应的 ID
                    if uuid:
                        self.message_get[uuid] = extracted_data  # 存储响应数据
                        print("返回数据...")
                        print(result)
                        self.pending_requests.discard(uuid)  # 移除已完成的请求 ID

                        # 检查所有请求是否已完成，如果完成则触发停止事件
                        if not self.pending_requests:
                            self.stop_event.set()
            except ValueError as e:
                print(f"Error decoding response: {e}")

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

    async def end(self):
        """发送 shutdown 和 exit 请求以关闭语言服务器"""
        await self.stop_event.wait()  # 等待所有请求完成
        print("关闭语言服务器...")
        if self.process:
            # 请求终止进程
            self.process.terminate()
            # 等待进程退出
            await self.process.wait()


# 主程序入口
if __name__ == "__main__":
    # 设置根目录 URI 和文件 URI
    rootUri = Path(
        r"D:\github\codebiu\server-example\src"
    ).as_uri()  # 生成文件的 URI 格式
    use_Uri = Path(
        r"D:\github\codebiu\server-example\src\utils\rag\graph_rag.py"
    ).as_uri()
    position_this = {"line": 273, "character": 44}  # 指定函数的行号和列号（示例位置）
    # 定义请求位置列表
    positions = [{"line": 273, "character": 44}, {"line": 273, "character": 44}]

    async def main():
        lsp = LspPythonPyright()

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
            "position": position_this,
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

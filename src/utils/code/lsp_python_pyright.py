import json
from pathlib import Path
import subprocess
from typing import Dict

file_path = Path(r"D:\github\codebiu\server-example\src")
rootUri = file_path.as_uri()  # 生成文件的 URI 格式
use_file_path = Path(r"D:\github\codebiu\server-example\src\utils\rag\graph_rag.py")
use_Uri = use_file_path.as_uri()  # 生成文件的 URI 格式
position = {"line": 273, "character": 44}  # 指定函数的行号和列号（示例位置）


class LspPythonPyright:

    def lsp_start(self):
        # 启动 pyright-langserver
        self.process = subprocess.Popen(
            # ["pyright-langserver", "--stdio"],
            ["D:/a_code_lib/conda_env/pc_py/Scripts/pyright-langserver.exe", "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def send_request(self, method: str, params: Dict, uuid):
        """发送 JSON-RPC 请求到语言服务器"""
        request = {"jsonrpc": "2.0", "id": uuid, "method": method, "params": params}
        # message = json.dumps(request) + "\n"
        message = json.dumps(request)  + "\n"
        if self.process.poll() is None:  # 子进程仍在运行
            self.process.stdin.write(message)
            self.process.stdin.flush()
        else:
            print("Subprocess has terminated, cannot send message.")

    def receive_response(self):
        """接收语言服务器的响应"""
        stdout, stderr = self.process.communicate()
        # response = json.loads(stdout)
        return stdout
        


if __name__ == "__main__":
    import uuid
    lspPythonPyright = LspPythonPyright()
    lspPythonPyright.lsp_start()
    response = lspPythonPyright.receive_response()
    print("start:", response)
    
    rootUri = Path(r"D:\github\codebiu\server-example\src").as_uri()  # 生成文件的 URI 格式
    use_Uri = Path(r"D:\github\codebiu\server-example\src\utils\rag\graph_rag.py").as_uri()
    position = {'line': 273, 'character': 44}  # 指定函数的行号和列号（示例位置）

    # 初始化请求
    initialize_params = {
        "processId": None,
        "rootUri": rootUri,
        "capabilities": {},
    }
    lspPythonPyright.send_request("initialize", initialize_params,str(uuid.uuid4()))
    response = lspPythonPyright.receive_response()
    print("Initialize Response:", response)

    # 查找函数定义
    definition_params = {
        "textDocument":  {'uri': use_Uri},
        "position": position,
    }
    lspPythonPyright.send_request("textDocument/definition", definition_params,str(uuid.uuid4()))
    response = lspPythonPyright.receive_response()
    print("Definition Response:", response)

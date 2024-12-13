import json
from pathlib import Path
import subprocess
from typing import Dict
#  dart language-server --diagnostic-port=8100
class LspDarkLanguageServer:

    def lsp_start(self):
        # 启动 pyright-langserver
        self.process = subprocess.Popen(
            [r"D:\a_code_lib\jdks\android\flutter_windows_3.24.5-stable\flutter\bin\cache\dart-sdk\bin\dart.exe",
             'language-server','--diagnostic-port=8100'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
                
        # 获取输出并解码
        stdout, stderr = self.process.communicate()

        # 输出标准输出和错误输出
        print("STDOUT:", stdout)
        print("STDERR:", stderr)

        # 等待进程结束并获取返回码
        exit_code = self.process.wait()
        print("Process exited with code:", exit_code)

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
    lspPythonPyright = LspDarkLanguageServer()
    lspPythonPyright.lsp_start()
    response = lspPythonPyright.receive_response()
    print("start:", response)
    
    rootUri = Path("D:/project/test/sdk-3.5.0/pkg/analysis_server/tool/spec").as_uri()  # 生成文件的 URI 格式
    use_Uri = Path("D:/project/test/sdk-3.5.0/pkg/analysis_server/tool/spec/check_all_test.dart").as_uri()
    position = {'line': 18, 'character': 31}  # 指定函数的行号和列号（示例位置）
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

import asyncio, json, subprocess, uuid
import time
from pathlib import Path
from config.log import logger
from utils.lsp import Lsp

global_var = 0


class LspDart(Lsp):
    async def impl(self, use_path: Path, line: int, character: int):
        """实现关系"""
        use_Uri = use_path.as_uri()
        message = {
            "textDocument": {"uri": use_Uri},
            "position": {"line": line, "character": character},
        }
        return await self._send("textDocument/implementation", message)


# 主程序入口
if __name__ == "__main__":
    # 设置根目录 URI 和文件 URI
    root_path = Path(r"D:\test\flutter_mall-master\lib")
    use_path = Path(
        r"D:\test\flutter_mall-master\lib\utils\http_util.dart"
    )
    # 定义请求位置列表
    positions = [
        # 101行的27列 字段左侧起始位置
        {"line": 100, "character": 26}
    ]

    async def main():
        lsp = LspDart()
        # 启动并初始化语言服务器
        await lsp.start([ "dart","language-server",], root_path)
        # 等待1s 验证返回非阻塞
        await asyncio.sleep(1)
        
        # 发送请求
        for position in positions:
            response = await lsp.references(use_path, position["line"], position["character"])
            # response = await response_future
            print("Response:", response)
        await lsp.stop()
        print('end')

asyncio.run(main())

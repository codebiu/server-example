import asyncio
from pathlib import Path
from typing import Any
from common.utils.lsp import Lsp

# type
StringDict = dict[str, Any]


class LspRuby(Lsp):

    async def references(self, use_path: Path, line, character):
        await super()._open_file(use_path)
        return await super().references(use_path, line, character)


# 主程序入口
if __name__ == "__main__":
    root_path = Path(
        "D:/project/dhc2024/LLM/llm_ai4se_code_analysis_assistant_backend/temp/5e579f66-9fb0-42f0-a882-5dc61c635481"
    )
    use_path = Path(
        "D:/project/dhc2024/LLM/llm_ai4se_code_analysis_assistant_backend/temp/5e579f66-9fb0-42f0-a882-5dc61c635481/app/controllers/address_books_controller.rb"
    )
    positions = [{"line": 40, "character": 8}, {"line": 150, "character": 7}]

    async def main():
        lsp = LspRuby()
        # 启动并初始化语言服务器
        await lsp.start(["D:\\a_code_lib\\Ruby33-x64\\bin\\solargraph.bat", "stdio"], root_path)
        # await lsp.start(["D:\\a_code_lib\\Ruby33-x64\\bin\\ruby-lsp.bat"], root_path)
        # 等待1s 验证返回非阻塞
        await asyncio.sleep(1)

        # 发送请求
        for position in positions:
            response = await lsp.references(
                use_path, position["line"], position["character"]
            )
            # response = await response_future
            print("Response:", response)
        await lsp.stop()
        print("end")

    asyncio.run(main())

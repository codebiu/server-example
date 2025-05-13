from pathlib import Path
import aiofiles

# import json


class FileUtils:
    # 异步读取文件并流式传输
    async def read_file_stream(
        file_path: Path,
        # 每次读取 1mb
        chunk_size: int = 1024 * 8,
    ):
        async with aiofiles.open(file_path, mode="rb") as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
                
    def write(out_file_path: str, content):
        """写入代码"""
        # 写入文件 没有就创建
        Path(out_file_path).parent.mkdir(parents=True, exist_ok=True)
        # 写入文件
        with open(out_file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    def read(file_path: str):
        """读取文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

# 文件类型和内容常见



# if __name__ == "__main__":
# current_dir = Path.cwd()  # 获取当前工作目录
# directory_tree = DirectoryTree(current_dir)
# directory_tree.build()
# # 将目录树转换为 JSON 格式
# json_tree = json.dumps(
#     directory_tree.tree,
#     #默认输出ASCLL码，False可以输出中文。
#     ensure_ascii=False,
# )
# print(json_tree)

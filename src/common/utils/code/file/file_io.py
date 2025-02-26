from pathlib import Path


class FileIO:    
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
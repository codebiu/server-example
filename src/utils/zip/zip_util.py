import zipfile
from pathlib import Path

def zip_full_path(out_path: str, paths: list):
    """
    压缩文件或文件夹
    :param out_path: 压缩文件保存的路径（包括文件名，例如 'archive.zip'）
    :param paths: 需要压缩的文件或文件夹路径的列表
    """
    # 确保输出路径所在目录存在
    out_dir = Path(out_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # 打开一个 zip 文件用于写入
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for path in paths:
            path = Path(path)
            # 如果路径是文件，则压缩文件
            if path.is_file():
                zipf.write(path, arcname=path.name)  # arcname 是压缩包中的文件名
            # 如果路径是文件夹，则压缩文件夹内的所有文件
            elif path.is_dir():
                for file in path.rglob('*'):  # rglob 遍历文件夹及其子文件夹
                    if file.is_file():
                        zipf.write(file, arcname=file.relative_to(path))  # 保留相对路径
            else:
                print(f"警告: {path} 既不是文件也不是目录，跳过")
    
    print(f"文件已成功压缩到: {out_path}")

if __name__ == "__main__":
    # 使用示例
    out_file_path = "output/archive.zip"
    files_and_dirs_to_zip = ["file1.txt", "file2.txt", "folder_to_compress"]

    zip_full_path(out_file_path, files_and_dirs_to_zip)

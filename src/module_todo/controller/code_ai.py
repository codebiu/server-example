import os
import json
from datetime import datetime
import chardet

def is_binary_file(filepath):
    """检查文件是否为二进制文件"""
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:  # 二进制文件通常包含null字节
                return True
            # 使用chardet检测编码
            result = chardet.detect(chunk)
            return result['encoding'] is None or result['confidence'] < 0.7
    except Exception:
        return True  # 如果无法读取，当作二进制文件处理

def read_file_content(filepath):
    """尝试以UTF-8读取文件内容，失败时尝试自动检测编码"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            # 尝试检测编码
            with open(filepath, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] if result['confidence'] > 0.7 else 'utf-8'
            with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                return f.read()
        except Exception:
            return None  # 无法读取内容
    except Exception:
        return None

def scan_directory(root_dir, target_files):
    """扫描目录树并收集匹配文件的信息"""
    result = {}
    target_files_set = set(target_files)  # 转换为集合提高查找效率
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename in target_files_set:
                filepath = os.path.join(dirpath, filename)
                try:
                    if is_binary_file(filepath):
                        continue  # 跳过二进制文件
                    
                    # 获取文件信息
                    stat = os.stat(filepath)
                    content = read_file_content(filepath)
                    
                    if content is None:  # 无法读取内容
                        continue
                    
                    # 计算相对路径
                    rel_path = os.path.relpath(filepath, start=root_dir)
                    
                    # 添加到结果
                    result[filename] = {
                        "路径": rel_path,
                        "内容": content,
                        "大小": stat.st_size,
                        "最后修改时间": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }
                except Exception as e:
                    print(f"处理文件 {filepath} 时出错: {str(e)}")
                    continue
    
    return result

def main():
    import sys
    import argparse
    
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='扫描目录并提取特定文件内容')
    parser.add_argument('root_dir', help='需要扫描的根目录路径')
    parser.add_argument('target_files', nargs='+', help='需要匹配的文件名列表')
    
    args = parser.parse_args()
    
    # 扫描目录
    result = scan_directory(args.root_dir, args.target_files)
    
    # 输出JSON结果
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
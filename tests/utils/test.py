from utils.ast.ast_languages import AstLanguages
from utils.enum.code import CodeType


if __name__ == "__main__":
    import time
    
    # 创建分割器
    chunker = AstLanguages()
    start_time = time.time()

    # 读取python文件到字符串
    # with open(r"D:\test\fastapi\routing.py", "r", encoding="utf-8") as f:
    with open(r"test-data\text\test.java", "r", encoding="utf-8") as f:
        text_str = f.read()
        print(time.time() - start_time)
        start_time = time.time()
        new_chunks = chunker.chunk(CodeType.java,text_str)
        # print(new_chunks)
        print(time.time() - start_time)
        start_time = time.time()

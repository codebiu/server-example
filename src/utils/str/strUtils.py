import gzip
import base64

# # 原始字符串
# original_string = "这是一个需要压缩的字符串这是一个需要压缩的字符串这是一个需要压缩的字符串"

# # 压缩
# compressed_bytes = gzip.compress(original_string.encode('utf-8'))
# compressed_string = base64.b64encode(compressed_bytes).decode('utf-8')
# print(f"Compressed string: {compressed_string}")

# # 解压缩
# decompressed_bytes = base64.b64decode(compressed_string)
# decompressed_string = gzip.decompress(decompressed_bytes).decode('utf-8')
# print(f"Decompressed string: {decompressed_string}")

# 自适应压缩
def compress_auto(original_string:str)->tuple[bool,bytes]:
    original_bytes = original_string.encode('utf-8')
    original_bytes_size = len(original_bytes)
    # 判断original_string长度 是否小于100 直接返回
    if original_bytes_size<100:
        return False, original_bytes
    # 压缩
    compressed_bytes = gzip.compress(original_string.encode('utf-8'))
    compressed_size = len(compressed_bytes)
    # 计算原始和压缩后的大小 判断是否压缩
    if compressed_size < original_bytes_size:
        # return True, compressed_bytes
        return True, compressed_bytes
    else:
        return False, original_bytes
    
# 解压缩
def decompress_auto(is_compressed,compressed_bytes)->bytes:
    if is_compressed:
        decompressed_bytes = gzip.decompress(compressed_bytes)
        # decompressed_string = decompressed_bytes.decode('utf-8')
        return decompressed_bytes
    else:
        return compressed_bytes


if __name__ == '__main__':
    def compress_and_calculate_ratio(original_string):
        # 压缩
        compressed_bytes = gzip.compress(original_string.encode('utf-8'))
        compressed_string = base64.b64encode(compressed_bytes).decode('utf-8')

        # 打印压缩后的字符串
        # print(f"Compressed string: {compressed_string}")

        # 计算压缩比
        original_size = len(original_string.encode('utf-8'))
        compressed_size = len(compressed_bytes)
        compression_ratio = compressed_size/original_size  if compressed_size != 0 else float('inf')

        print(f"Original size: {original_size} bytes")
        print(f"Compressed size: {compressed_size} bytes")
        print(f"ratio: {compression_ratio:.2f}")

        # 解压缩
        decompressed_bytes = gzip.decompress(base64.b64decode(compressed_string))
        decompressed_string = decompressed_bytes.decode('utf-8')

        # 打印解压缩后的字符串
        # print(f"Decompressed string: {decompressed_string}")

    # 测试短字符串
    short_string = "这是一个需要压缩的字符串"
    print("Short String:")
    compress_and_calculate_ratio(short_string)

    # 测试长字符串
    long_string = """
    非常短的字符串压缩后数据可能会比原始数据更大。压缩算法在压缩数据时会添加一些额外的元数据（如头部信息），
    这些元数据可能会占据更多的空间，特别是在数据量较小的情况下。

    解释
    元数据开销：gzip 压缩格式包含一些固定的头部信息，这些信息通常占用了几十个字节。
    对于短字符串，这些额外的元数据可能会使压缩后的数据比原始数据更大。
    压缩效率：对于较长的数据，压缩算法可以找到更多的重复模式并有效地减少数据量。
    但对于短字符串，压缩算法可能无法找到足够的重复模式来显著减少数据量。
    """
    print("\nLong String:")
    compress_and_calculate_ratio(long_string)
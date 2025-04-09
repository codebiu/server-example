from bs4 import UnicodeDammit
from typing import Union, Optional, List, ByteString
from pathlib import Path
import warnings


class EncodingDetector:
    """
    编码检测与转换类，支持文件和字节数据的编码检测与转换

    功能：
    1. 自动检测文件或字节数据的编码
    2. 将内容转换为指定编码
    3. 提供编码检测结果信息

    示例:
        >>> # 文件编码检测
        >>> detector = EncodingDetector("path/to/file.txt")
        >>> print(detector.detect_encoding())

        >>> # 字节数据检测
        >>> print(EncodingDetector.get_chunk_content("你好".encode("gbk")))
    """

    def __init__(
        self,
        content: Union[str, bytes, Path],
        override_encodings: Optional[List[str]] = None,
        max_file_size: Optional[int] = None,
    ):
        """
        初始化编码检测器

        :param content: 要检测的内容，可以是文件路径、字节数据或字符串
        :param override_encodings: 优先尝试的编码列表（可选）
        :param max_file_size: 最大读取文件大小（字节），None表示读取全部
        """
        self.original_content = content
        self.override_encodings = override_encodings
        self._dammit = None
        self.max_file_size = max_file_size

        try:
            if isinstance(content, (str, Path)):
                path = Path(content)
                if path.is_file():
                    self._raw_data = self._read_file_smart(path)
                else:
                    self._raw_data = (
                        content.encode("utf-8") if isinstance(content, str) else content
                    )
            else:
                self._raw_data = content

            self._analyze()
        except Exception as e:
            raise ValueError(f"初始化失败: {str(e)}") from e

    def _read_file_smart(self, path: Path) -> bytes:
        """智能读取文件，可选限制大小"""
        if self.max_file_size:
            with path.open("rb") as f:
                return f.read(self.max_file_size)
        return path.read_bytes()

    def _analyze(self):
        """分析内容并确定编码"""
        try:
            self._dammit = UnicodeDammit(
                self._raw_data, override_encodings=self.override_encodings
            )
        except Exception as e:
            warnings.warn(f"编码分析失败: {str(e)}")
            raise

    def detect_encoding(self) -> str:
        """检测并返回内容的编码"""
        return self._dammit.original_encoding

    def get_content(self, encoding: Optional[str] = None) -> str:
        """
        获取内容文本

        :param encoding: 指定编码（可选），若为None则使用检测到的编码
        :return: 解码后的文本内容
        :raises: UnicodeDecodeError 当解码失败时
        """
        try:
            if encoding:
                return self._raw_data.decode(encoding)
            return self._dammit.unicode_markup
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                f"无法用编码 {encoding or self.detect_encoding()} 解码内容"
            ) from e

    @classmethod
    def get_chunk_content(
        cls, data: ByteString, encoding: Optional[str] = None, max_size: int = 65536
    ) -> str:
        """
        快速检测字节数据的编码并返回文本内容

        :param data: 要检测的字节数据
        :param encoding: 指定编码（可选）
        :param max_size: 最大检测大小（字节）
        :return: 解码后的文本内容
        """
        if len(data) > max_size:
            data = data[:max_size]
        return cls(data).get_content(encoding)

    def __str__(self) -> str:
        return f"EncodingDetector(encoding={self.detect_encoding()}, length={len(self.get_content())})"


if __name__ == "__main__":
    # 示例1: 文件编码检测
    import time

    test_file = [
        r"test-data\text\encoder\utf8.txt",
        r"test-data\text\encoder\shift_jis.txt",
    ]
    for file in test_file:
        print(f"检测文件: {file}")
        start_time = time.time()
        try:
            # 只读取前1KB用于检测
            encoder = EncodingDetector(file, max_file_size=1024)
            print(encoder.detect_encoding())
            print(encoder.get_content())
            print(f"耗时: {time.time() - start_time:.2f}秒")
        except Exception as e:
            print(f"错误: {str(e)}")

    # 示例2: 字节数据检测
    test_cases = [
        ("你好QWEQWEQWEQWE解析单个代码文件".encode("gbk"), None),
        ("こんにちはこんにちはこんにちはこんにちは".encode("shift_jis"), None),
        ("你好".encode("utf-8"), None),
    ]

    for data, enc in test_cases:
        try:
            print(EncodingDetector.get_chunk_content(data, enc))
        except Exception as e:
            print(f"解码失败: {str(e)}")

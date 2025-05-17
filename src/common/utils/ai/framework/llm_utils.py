import numpy as np
import re

class LLMUtils:
    
    def count_tokens_universal(self, text):
        """
        通用的token计数器，支持中英日文和标点符号。
        :param text: 输入的文本
        :return: token的数量
        """
        # 正则表达式匹配：
        # 1. 中文字符（包括汉字）
        # 2. 日文字符（平假名、片假名、日文汉字）
        # 3. 英文字符（单词）
        # 4. 标点符号（中英文标点）
        # 5. 其他字符（如数字、特殊符号等）
        tokens = re.findall(
            r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]|\w+|[^\w\s]", text, re.UNICODE
        )
        # 返回token的数量
        return len(tokens)
    def clean_prompt(prompt: str) -> str:
        # 移除多余空格、换行等
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        return prompt
        

    @staticmethod
    def embeddings_info(embeddings_result):
        """_summary_: 获取向量化模型信息

        Args:
            embeddings_result (_type_): 

        Returns:
            _type_: _description_
        """
        vector = np.array(embeddings_result)  # 转换为 NumPy 数组
        norm = np.linalg.norm(vector)  # 计算 L2 范数
        # 判断是否归一化
        tolerance = 1e-6  # 设置容差范围，处理浮点数精度问题
        is_normalized_bool = abs(norm - 1.0) < tolerance
        return {
            # 归一化
            "norm": norm,
            "normalized": is_normalized_bool,
            # 维度
            "len": len(vector),
        }

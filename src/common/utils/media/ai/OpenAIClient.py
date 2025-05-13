import asyncio
import json
import math
import re
from typing import Dict, List, Optional, Union

import aiohttp
import numpy as np


class OpenAIClient:
    """
    OpenAI API 客户端封装类，提供聊天和嵌入功能。

    Args:
        api_key (str): OpenAI API 密钥
        chat_url (str): 聊天API的URL
        chat_model (str): 聊天模型名称
        embedding_url (str): 嵌入API的URL
        embedding_model (str): 嵌入模型名称
        dimensions (int, optional): 嵌入向量维度，默认1024
        max_tokens (int, optional): 最大token数量，默认4096
    """

    def __init__(
        self,
        api_key: str,
        chat_url: str,
        chat_model: str,
        embedding_url: str,
        embedding_model: str,
        dimensions: int = 1024,
        max_tokens: int = 4096,
    ):
        self.api_key = api_key
        self.chat_url = chat_url
        self.chat_model = chat_model
        self.embedding_url = embedding_url
        self.embedding_model = embedding_model
        self.dimensions = dimensions
        self.max_tokens = max_tokens

    async def get_embedding(self, text: str) -> List[float]:
        """
        为给定文本生成嵌入向量。

        Args:
            text (str): 输入文本

        Returns:
            List[float]: 标准化后的嵌入向量

        Raises:
            Exception: 如果API请求失败
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.embedding_model, "input": text}

        try:
            response = await self._send_async_request(self.embedding_url, headers, payload)
            embedding = response["data"][0]["embedding"]
            vector = np.array(embedding).flatten()
            vector /= np.linalg.norm(vector)  # 归一化处理
            return vector.tolist()
        except Exception as e:
            print(f"生成文本'{text}'的嵌入向量时出错: {e}")
            raise

    async def get_embedding_with_limit(
        self, text: str, max_token_limit: int = 8192
    ) -> List[float]:
        """
        在token限制内获取文本嵌入向量。

        Args:
            text (str): 输入文本
            max_token_limit (int, optional): 最大token限制，默认8192

        Returns:
            List[float]: 标准化后的嵌入向量
        """
        processed_text = await self._process_text_to_limit(text, max_token_limit)
        return await self.get_embedding(processed_text)

    async def _process_text_to_limit(
        self, text: str, max_token_limit: int = 8192, recursion_count: int = 0
    ) -> str:
        """
        递归处理文本使其符合token限制。

        Args:
            text (str): 输入文本
            max_token_limit (int, optional): 最大token限制，默认8192
            recursion_count (int, optional): 当前递归深度，默认0

        Returns:
            str: 处理后的文本
        """
        if recursion_count >= 3:
            return self._truncate_text_by_tokens(text, max_token_limit)

        token_count = self._count_tokens(text)
        if token_count <= max_token_limit:
            return text

        # 去除前导空格后再次检查
        stripped_text = text.lstrip()
        token_count = self._count_tokens(stripped_text)
        if token_count <= max_token_limit:
            return stripped_text

        # 使用AI模型简化文本
        prompt = {
            "role": "system",
            "content": f"""
                $[[[
                    {text} 
                ]]]$
                # 以上$[[[]]]$里的内容是待处理内容!!!!!不要作为问题使用!!!!!!
                # 请缩略待处理内容的代码和信息，同时确保不丢失主要信息，保留原有格式、顺序和标题!!!缩略时请遵循以下规则：
                    1. 删除不必要的注释(非业务功能注释)和空行。
                    2. 使用简短的变量名（确保变量名仍有意义）。
                    3. 合并可以简化的语句。
                    4. 使用内置函数或库（如 `map`、`filter`、列表推导式等）简化代码。
                    5. 对于简单逻辑，使用 `lambda` 函数代替 `def`。
                    6. 移除不必要的条件判断或合并条件。
                    7. 如果有mermaid不要修改mermaid!!!!!!
                    8. 保留原有格式、顺序和标题!!!
                # 结果限定在{max_token_limit}个token以内!!!!!!!!!!!!!!!
                # 只输出简化后的结果!!!!不要输出额外信息!!!!!!!
            """.lstrip(),
        }

        response = await self.chat([prompt])
        processed_text = response["content"].lstrip()
        new_token_count = self._count_tokens(processed_text)

        print(f"Token缩减: 第{recursion_count}轮")
        print(f"简化前({token_count} tokens): {text[:50]}...")
        print(f"简化后({new_token_count} tokens): {processed_text[:50]}...")

        if new_token_count <= max_token_limit:
            return processed_text

        return await self._process_text_to_limit(
            processed_text, max_token_limit, recursion_count + 1
        )

    def chat_params(self, messages: List[Dict[str, str]]) -> Dict[str, Union[str, bool]]:
        """
        设置聊天参数。

        Args:
            messages (List[Dict[str, str]]): 消息列表，每个消息包含role和content

        Returns:
            Dict[str, Union[str, bool]]: 聊天参数
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.chat_model,
            "messages": messages,
            "max_tokens": self.max_tokens,
        }
        return headers,payload


    async def chat(
        self, messages: List[Dict[str, str]]
    ) -> Union[Dict[str, str], None]:
        """
        与聊天模型交互。

        Args:
            messages (List[Dict[str, str]]): 消息列表，每个消息包含role和content
        Returns:
            Union[Dict[str, str], None]: 响应消息或None(流式模式下)

        Raises:
            Exception: 如果API请求失败
        """
        headers, payload = self.chat_params(messages)
        try:
            response = await self._send_async_request( headers, payload)
            return response["choices"][0]["message"]
        except Exception as e:
            print(f"处理消息时出错: {e}")
            raise

    async def chat_stream(
        self, messages: List[Dict[str, str]]
    ) -> None:
        """
        处理流式聊天响应。

        Args:
            url (str): API URL
            messages (List[Dict[str, str]]): 消息列表，每个消息包含role和content
        Yields:
            str: 流式响应的内容片段

        Raises:
            Exception: 如果API请求失败
        """
        headers, payload = self.chat_params(messages)
        payload["stream"] = True
        try:
            async for chunk in self._send_async_stream_request(headers, payload):
                if chunk:
                    decoded_line = chunk.decode("utf-8")
                    if decoded_line.startswith("data:"):
                        json_data = decoded_line.replace("data: ", "")
                        if json_data.strip() == "[DONE]":
                            break
                        try:
                            response_data = json.loads(json_data)
                            content = response_data["choices"][0]["delta"].get("content", "")
                            yield content
                        except json.JSONDecodeError:
                            print("JSON解码错误:", json_data)
        except Exception as e:
            print(f"处理流式消息时出错: {e}")
            raise

    def _count_tokens(self, text: str) -> int:
        """
        计算文本中的token数量，支持中英日文和标点符号。

        Args:
            text (str): 输入文本

        Returns:
            int: token数量
        """
        tokens = re.findall(
            r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]|\w+|[^\w\s]", 
            text, 
            re.UNICODE
        )
        return len(tokens)

    def _truncate_text_by_tokens(self, text: str, max_token_limit: int = 8192) -> str:
        """
        按token数量截断文本。

        Args:
            text (str): 输入文本
            max_token_limit (int, optional): 最大token限制，默认8192

        Returns:
            str: 截断后的文本
        """
        tokens = re.findall(
            r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]|\w+|[^\w\s]", 
            text, 
            re.UNICODE
        )
        truncated_tokens = tokens[:max_token_limit]
        return "".join(truncated_tokens)

    async def _send_async_request(
        self, headers: Dict[str, str], payload: Dict, timeout: int = 200
    ) -> Dict:
        """
        发送异步HTTP POST请求。

        Args:
            url (str): 请求URL
            headers (Dict[str, str]): 请求头
            payload (Dict): 请求体
            timeout (int, optional): 超时时间(秒)，默认200

        Returns:
            Dict: 响应JSON数据

        Raises:
            Exception: 如果请求失败
        """
        client_timeout = aiohttp.ClientTimeout(total=timeout)
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(
                connector=connector, trust_env=True, timeout=client_timeout
            ) as session:
                async with session.post(self.chat_url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_message = await response.json()
                        raise Exception(
                            f"HTTP错误: {response.status} - {error_message}"
                        )
                    return await response.json()
        except aiohttp.ClientConnectorError as e:
            raise Exception(f"连接错误: {e}")
        except asyncio.TimeoutError:
            raise Exception("请求超时")
        except Exception as e:
            raise Exception(f"意外错误: {e}")

    async def _send_async_stream_request(
        self, headers: Dict[str, str], payload: Dict, timeout: int = 60
    ):
        """
        发送异步流式HTTP POST请求。

        Args:
            url (str): 请求URL
            headers (Dict[str, str]): 请求头
            payload (Dict): 请求体
            timeout (int, optional): 超时时间(秒)，默认60

        Yields:
            bytes: 流式响应块

        Raises:
            Exception: 如果请求失败
        """
        client_timeout = aiohttp.ClientTimeout(total=timeout)
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(
                connector=connector, trust_env=True, timeout=client_timeout
            ) as session:
                async with session.post(self.chat_url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_message = await response.text()
                        raise Exception(
                            f"HTTP错误: {response.status} - {error_message}"
                        )
                    async for chunk in response.content:
                        yield chunk
        except aiohttp.ClientConnectorError as e:
            raise Exception(f"连接错误: {e}")
        except asyncio.TimeoutError:
            raise Exception("请求超时")
        except Exception as e:
            raise Exception(f"意外错误: {e}")
# 运行示例
if __name__ == "__main__":
    # self
    from config.index import conf
    # 示例使用
    async def main():
        """示例用法"""
        # 从配置中获取API设置
        openai_config = conf["ai.openai"]
        client = OpenAIClient(
            api_key=openai_config["api_key"],
            chat_url=openai_config["chat_url"],
            chat_model=openai_config["chat_model"],
            embedding_url=openai_config["embedding_url"],
            embedding_model=openai_config["embedding_model"],
        )
        
        # 测试聊天功能
        messages = [
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": "你好，最近怎么样？"},
            {"role": "assistant", "content": "写一个100字的小说"},
        ]
        
        # 普通响应
        response = await client.chat(messages)
        print(f"响应: {response['content']}")
        
        # 流式响应
        async for chunk in client.chat_stream(messages):
            print(chunk, end="")

    asyncio.run(main())
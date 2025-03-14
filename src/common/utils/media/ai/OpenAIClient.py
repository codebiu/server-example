import asyncio
import numpy as np
import requests
# from typing import List, Dict


class OpenAIClient:
    """
        初始化 OpenAIClient 实例。

        :param api_key: OpenAI API 密钥
        :param chat_model: 用于聊天的模型名称
        :param embedding_model: 用于生成嵌入的模型名称
        :param dimensions: 嵌入向量的维度，默认为 1024
        :param max_tokens: 最大 token 数量，默认为 4096
    """
    def __init__(
            self,
            api_key: str,
            chat_url: str,
            chat_model: str,
            embedding_url: str,
            embedding_model: str,
            dimensions: int = 1024,
            max_tokens: int = 4096
    ):
        self.api_key = api_key
        self.chat_url = chat_url
        self.chat_model = chat_model
        self.embedding_url = embedding_url
        self.embedding_model = embedding_model
        self.dimensions = dimensions
        self.max_tokens = max_tokens

    async def embedding(self, text: str) -> list[float]:
        """
            生成给定文本的嵌入向量。

            :param text: 输入文本
            :return: 标准化的嵌入向量
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.embedding_model,
            "input": text
        }

        try:
            response = await self._send_request(self.embedding_url, headers, data)
            if response.status_code == 200:
                embedding = response.json()["data"][0]["embedding"]
                vector = np.array(embedding).flatten()
                vector /= np.linalg.norm(vector)
                return vector.tolist()
            else:
                raise Exception(f"Error generating embedding: {response.text}")
        except Exception as e:
            print(f"Error generating embedding for text '{text}': {e}")
            raise

    async def invoke(self, messages: list[dict[str, str]]) -> list[str, str]:
        """
            发送消息并获取响应。

            :param messages: 消息列表，每个消息是一个字典，包含角色和内容
            :return: 响应消息
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.chat_model,
            "messages": messages,
            "max_tokens": self.max_tokens
        }

        try:
            response = await self._send_request(self.chat_url, headers, data)
            if response.status_code == 200:
                response_data = response.json()
                return response_data["choices"][0]["message"]
            else:
                raise Exception(f"Error processing messages: {response.text}")
        except Exception as e:
            print(f"Error processing messages: {e}")
            raise
    async def _send_request(self, url: str, headers: dict, data: dict) -> requests.Response:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: requests.post(url, headers=headers, json=data))


# 运行示例
if __name__ == "__main__":
    # self
    from config.index import conf
    # 示例使用
    async def main():
   # 获取ai_api
        # openai_set = conf["ai"]["openai"]
        openai_set = conf["ai"]["aihubmix"]
        client = OpenAIClient(
            api_key=openai_set["api_key"],
            chat_url=openai_set["chat_url"],
            chat_model=openai_set["chat_model"],
            embedding_url=openai_set["embedding_url"],
            embedding_model=openai_set["embedding_model"],
        )
        # 测试 embedding 方法
        text = "Hello, how are you?"
        embedding = await client.embedding(text)
        print(f"Embedding: {embedding}")

        # 测试 invoke 方法
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "Hi, I'm doing well! How can I help you today?"}
        ]
        response_message = await client.invoke(messages)
        print(f"Response: {response_message['content']}")

    asyncio.run(main())
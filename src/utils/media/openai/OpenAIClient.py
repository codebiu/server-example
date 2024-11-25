import asyncio
import numpy as np
from typing import List, Generator, Optional
from pathlib import Path
from langchain_core.messages import BaseMessage
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


class OpenAIClient:
    def __init__(
            self,
            api_key: str,
            chat_model: str,
            embedding_model: str,
            dimensions: int = 1024,
            max_tokens: int = 4096
    ):
        self.embedding_model = OpenAIEmbeddings(
            openai_api_key=api_key,
            model=embedding_model,
            dimensions=dimensions
        )
        self.chat_model = ChatOpenAI(
            openai_api_key=api_key,
            model=chat_model,
            max_tokens=max_tokens
        )

    async def embedding(self, text: str) -> List[float]:
        try:
            embedding = await self.embedding_model.aembed_query(text)
            vector = np.array(embedding).flatten()
            vector /= np.linalg.norm(vector)
            return vector.tolist()
        except Exception as e:
            print(f"Error generating embedding for text '{text}': {e}")
            raise

    async def invoke(self, messages: List[BaseMessage]) -> BaseMessage:
        try:
            response = await self.chat_model.ainvoke(messages)
            print("Messages processed successfully")
            return response
        except Exception as e:
            print(f"Error processing messages: {e}")
            raise

def iter_folder(path: Path) -> Generator[Path, None, None]:
    for p in path.iterdir():
        if p.is_dir():
            yield p
            yield from iter_folder(p)
        else:
            yield p

# 示例使用
async def main():
    api_key = "your_openai_api_key"
    chat_model = "gpt-3.5-turbo"
    embedding_model = "text-embedding-ada-002"

    client = OpenAIClient(
        api_key=api_key,
        chat_model=chat_model,
        embedding_model=embedding_model
    )

    # 测试 embedding 方法
    text = "Hello, how are you?"
    embedding = await client.embedding(text)
    print(f"Embedding: {embedding}")

    # 测试 invoke 方法
    messages = [
        BaseMessage(role="system", content="You are a helpful assistant."),
        BaseMessage(role="user", content="Hello, how are you?"),
        BaseMessage(role="assistant", content="Hi, I'm doing well! How can I help you today?")
    ]
    response_message = await client.invoke(messages)
    print(f"Response: {response_message.content}")

# 运行示例
if __name__ == "__main__":
    asyncio.run(main())
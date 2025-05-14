import asyncio
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# 正确初始化
llm = ChatOllama(
    model="qwen2.5:1.5b",
    base_url="http://localhost:11434",
    temperature=0.3,
    timeout=10  # 增加超时
)




# 使用示例
if __name__ == "__main__":
    async def main():
            # 正确调用方式
        messages = [HumanMessage(content="1+1=?")]
        response = llm.invoke(messages)
        print(response)

    asyncio.run(main())


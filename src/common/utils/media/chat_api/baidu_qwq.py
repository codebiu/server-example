import aiohttp
import json
from config.index import conf 

class AsyncChatBaidu:
    def __init__(self, API_KEY, SECRET_KEY) -> None:
        self.url = "https://qianfan.baidubce.com/v2/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "appid": API_KEY,
            "Authorization": f"Bearer {SECRET_KEY}",
        }

    async def ask(self, ask_dict):
        """普通异步请求方法"""
        ask_dict.update({
            "model": "qwq-32b",
            "web_search": {
                "enable": False,
                "enable_citation": False,
                "enable_trace": False
            }
        })
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                headers=self.headers,
                data=json.dumps(ask_dict)
            ) as response:
                return await response.text()

    async def ask_stream(self, ask_dict):
        """流式异步请求方法"""
        ask_dict.update({
            "model": "qwq-32b",
            "web_search": {
                "enable": False,
                "enable_citation": False,
                "enable_trace": False
            },
            "stream": True
        })

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                headers=self.headers,
                data=json.dumps(ask_dict)
            ) as response:
                
                is_thinking = True
                async for chunk in response.content:
                    if chunk:
                        return_json = chunk.decode("utf-8").strip()
                        
                        if return_json.startswith('data: '):
                            return_json = return_json[6:].strip()
                        if return_json == "[DONE]":
                            break
                        try:
                            data = json.loads(return_json)
                            if "error" in data:
                                yield data["error"].get("message", "")
                                break
                            for choice in data.get("choices", []):
                                delta = choice.get("delta", {})
                                
                                # 优先返回推理内容
                                if reasoning := delta.get("reasoning_content"):
                                    yield reasoning
                                    
                                if content := delta.get("content"):
                                    if is_thinking:
                                        is_thinking = False
                                        yield "*$result:$*"
                                    yield content
                                    
                        except json.JSONDecodeError:
                            yield f"JSON解析失败: {return_json}"
if __name__ == "__main__":
    # 使用示例
    async def main():
        test_ask = {
            "messages": [
                {
                    "role": "system",
                    "content": """你是一个专业的编码助手。使用markdown格式回答，用"###"标记结论标题。"""
                },
                {
                    "role": "user",
                    "content": "使用tree-sitter创建JCL语法解析器"
                }
            ]
        }
        
        chat = AsyncChatBaidu(
            conf["ai"]["baidu_ai_qwq"]["api_key"],
            conf["ai"]["baidu_ai_qwq"]["secret_key"]
        )
        
        # 流式调用
        async for chunk in chat.ask_stream(test_ask):
            print(chunk, end="")

    # 运行示例
    import asyncio
    asyncio.run(main())
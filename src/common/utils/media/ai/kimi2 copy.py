from typing import *
 
import os
import json
 
from openai import OpenAI
from openai.types.chat.chat_completion import Choice

 
client = OpenAI(
)
 
 
# search 工具的具体实现，这里我们只需要返回参数即可
def search_impl(arguments: Dict[str, Any]) -> Any:
    """
    在使用 Moonshot AI 提供的 search 工具的场合，只需要原封不动返回 arguments 即可，
    不需要额外的处理逻辑。
 
    但如果你想使用其他模型，并保留联网搜索的功能，那你只需要修改这里的实现（例如调用搜索
    和获取网页内容等），函数签名不变，依然是 work 的。
 
    这最大程度保证了兼容性，允许你在不同的模型间切换，并且不需要对代码有破坏性的修改。
    """
    return arguments
 

 
def main():
    messages = [
        {"role": "system", "content": "你是 Kimi。"},
    ]
 
    # 初始提问
    messages.append({
        "role": "user",
        "content": "搜索一下，最早一班北京到上海的后天航班。"
    })
    
    completion = client.chat.completions.create(
        model="moonshot-v1-128k",
        messages=messages,
        temperature=0.3,
        tools=[
            {
                "type": "builtin_function",  # <-- 使用 builtin_function 声明 $web_search 函数，请在每次请求都完整地带上 tools 声明
                "function": {
                    "name": "$web_search",
                },
            }
        ],
        stream=True,
    )
    for chunk in completion:
        # 在这里，每个 chunk 的结构都与之前的 completion 相似，但 message 字段被替换成了 delta 字段
        delta = chunk.choices[0].delta # <-- message 字段被替换成了 delta 字段
    
        if delta.content:
            # 我们在打印内容时，由于是流式输出，为了保证句子的连贯性，我们不人为地添加
            # 换行符，因此通过设置 end="" 来取消 print 自带的换行符。
            print(delta.content, end="")
        
    
 
 
 
if __name__ == '__main__':
    main()
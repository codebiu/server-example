import os
import json
import httpx  # 我们使用 httpx 库来执行我们的 HTTP 请求
 
tools = [
    {
        "type": "function",  # 约定的字段 type，目前支持 function 作为值
        "function": {  # 当 type 为 function 时，使用 function 字段定义具体的函数内容
            "name": "search",  # 函数的名称，请使用英文大小写字母、数据加上减号和下划线作为函数名称
            "description": """ 
				通过搜索引擎搜索互联网上的内容。
 
				当你的知识无法回答用户提出的问题，或用户请求你进行联网搜索时，调用此工具。请从与用户的对话中提取用户想要搜索的内容作为 query 参数的值。
				搜索结果包含网站的标题、网站的地址（URL）以及网站简介。
			""",  # 函数的介绍，在这里写上函数的具体作用以及使用场景，以便 Kimi 大模型能正确地选择使用哪些函数
            "parameters": {  # 使用 parameters 字段来定义函数接收的参数
                "type": "object",  # 固定使用 type: object 来使 Kimi 大模型生成一个 JSON Object 参数
                "required": ["query"],  # 使用 required 字段告诉 Kimi 大模型哪些参数是必填项
                "properties": {  # properties 中是具体的参数定义，你可以定义多个参数
                    "query": {  # 在这里，key 是参数名称，value 是参数的具体定义
                        "type": "string",  # 使用 type 定义参数类型
                        "description": """
							用户搜索的内容，请从用户的提问或聊天上下文中提取。
						"""  # 使用 description 描述参数以便 Kimi 大模型更好地生成参数
                    }
                }
            }
        }
    },
]
 
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer sk-GZcOwtHTE0UU9694OTp6kULM9Jz8XOQsN0AYUm3XsmIbIzxZ",
}
 
data = {
    "model": "moonshot-v1-128k",
    "messages": [
        {"role": "user", "content": "请联网搜索 最早一班北京到上海的后天航班。"}
    ],
    "temperature": 0.3,
    "stream": True,
    "n": 2,  # <-- 注意这里，我们要求 Kimi 大模型输出 2 个回复
    "tools": tools,  # <-- 添加工具调用
}
 
# 使用 httpx 向 Kimi 大模型发出 chat 请求，并获得响应 r
r = httpx.post("https://api.moonshot.cn/v1/chat/completions",
               headers=header,
               json=data)
if r.status_code != 200:
    raise Exception(r.text)
 
data: str
 
# 在这里，我们预先构建一个 List，用于存放不同的回复消息，由于我们设置了 n=2，因此我们将 List 初始化为 2 个元素
messages = [{}, {}]
 
# 在这里，我们使用了 iter_lines 方法来逐行读取响应体
for line in r.iter_lines():
    # 去除每一行收尾的空格，以便更好地处理数据块
    line = line.strip()
 
    # 接下来我们要处理三种不同的情况：
    #   1. 如果当前行是空行，则表明前一个数据块已接收完毕（即前文提到的，通过两个换行符结束数据块传输），我们可以对该数据块进行反序列化，并打印出对应的 content 内容；
    #   2. 如果当前行为非空行，且以 data: 开头，则表明这是一个数据块传输的开始，我们去除 data: 前缀后，首先判断是否是结束符 [DONE]，如果不是，将数据内容保存到 data 变量；
    #   3. 如果当前行为非空行，但不以 data: 开头，则表明当前行仍然归属上一个正在传输的数据块，我们将当前行的内容追加到 data 变量尾部；
 
    if len(line) == 0:
        chunk = json.loads(data)
 
        # 通过循环获取每个数据块中所有的 choice，并获取 index 对应的 message 对象
        for choice in chunk["choices"]:
            index = choice["index"]
            message = messages[index]
            usage = choice.get("usage")
            if usage:
                message["usage"] = usage
            delta = choice["delta"]
            role = delta.get("role")
            if role:
                message["role"] = role
            content = delta.get("content")
            if content:
            	if "content" not in message:
            		message["content"] = content
            	else:
                	message["content"] = message["content"] + content
 
            # 从这里，我们开始处理 tool_calls
            tool_calls = delta.get("tool_calls")  # <-- 先判断数据块中是否包含 tool_calls
            if tool_calls:
                if "tool_calls" not in message:
                    message["tool_calls"] = []  # <-- 如果包含 tool_calls，我们初始化一个列表来保存这些 tool_calls，注意此时的列表中没有任何元素，长度为 0
                for tool_call in tool_calls:
                    tool_call_index = tool_call["index"]  # <-- 获取当前 tool_call 的 index 索引
                    if len(message["tool_calls"]) < (
                            tool_call_index + 1):  # <-- 根据 index 索引扩充 tool_calls 列表，以便于我们能通过下标访问到对应的 tool_call
                        message["tool_calls"].extend([{}] * (tool_call_index + 1 - len(message["tool_calls"])))
                    tool_call_object = message["tool_calls"][tool_call_index]  # <-- 根据下标访问对应的 tool_call
                    tool_call_object["index"] = tool_call_index
 
                    # 下面的步骤，是根据数据块中的信息填充每个 tool_call 的 id、type、function 字段
                    # 在 function 字段中，又包括 name 和 arguments 字段，arguments 字段会由每个数据块
                    # 依次补充，如同 delta.content 字段一般。
 
                    tool_call_id = tool_call.get("id")
                    if tool_call_id:
                        tool_call_object["id"] = tool_call_id
                    tool_call_type = tool_call.get("type")
                    if tool_call_type:
                        tool_call_object["type"] = tool_call_type
                    tool_call_function = tool_call.get("function")
                    if tool_call_function:
                        if "function" not in tool_call_object:
                            tool_call_object["function"] = {}
                        tool_call_function_name = tool_call_function.get("name")
                        if tool_call_function_name:
                            tool_call_object["function"]["name"] = tool_call_function_name
                        tool_call_function_arguments = tool_call_function.get("arguments")
                        if tool_call_function_arguments:
                            if "arguments" not in tool_call_object["function"]:
                                tool_call_object["function"]["arguments"] = tool_call_function_arguments
                            else:
                                tool_call_object["function"]["arguments"] = tool_call_object["function"][
                                                                            "arguments"] + tool_call_function_arguments  # <-- 依次补充 function.arguments 字段的值
                    message["tool_calls"][tool_call_index] = tool_call_object
 
            data = ""  # 重置 data
    elif line.startswith("data: "):
        data = line.lstrip("data: ")
 
        # 当数据块内容为 [DONE] 时，则表明所有数据块已发送完毕，可断开网络连接
        if data == "[DONE]":
            break
    else:
        data = data + "\n" + line  # 我们仍然在追加内容时，为其添加一个换行符，因为这可能是该数据块有意将数据分行展示
 
# 在组装完所有 messages 后，我们分别打印其内容
for index, message in enumerate(messages):
    print("index:", index)
    print("message:", json.dumps(message, ensure_ascii=False))
    print("")
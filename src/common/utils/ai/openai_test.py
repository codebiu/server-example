import requests
import json

# 设置 API 密钥和 API 端点
api_key = ""
api_endpoint = "https://api.openai-proxy.com/v1/chat/completions"
# api_endpoint = "https://api.openai.com/v1/chat/completions"

# 准备请求的数据
data = {
        "model": "gpt-4",
        # "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": "You are a helpful assistant."},
                     {"role": "user", "content": "Say this is a test!"}],
        "temperature": 0.7
}
# data = {
#     "prompt": "Once upon a time",
#     "max_tokens": 50
# }

# 设置请求头，包括 API 密钥
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# 发送 POST 请求到 API 端点
response = requests.post(api_endpoint, headers=headers, json=data)

# 检查响应是否成功
if response.status_code == 200:
    # 解析并输出生成的文本
    result = response.json()
    generated_text = result["choices"][0]["text"].strip()
    print(generated_text)
else:
    print("Error:", response.text)

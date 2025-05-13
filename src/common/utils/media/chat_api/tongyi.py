import base64
import requests
import json

# 读取本地 图片转base64
def read_image(image_path):
    with open(image_path, "rb") as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode("utf-8")


base64_image = read_image('test.png')
dataImage = f"data:image/jpeg;base64,{base64_image}"
# 问题
test_ask = {
    "input": {
        "messages":[      
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "你是谁？"
            }
        ]
    }
}


class ChatTongyi:
    token: str
    url: str

    def __init__(self, API_KEY) -> None:
        # zhipu
        self.url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        # head
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        }

    def ask(self, ask_dict: dict):
        ask_dict["model"] = "qwen-max-latest"
        payload = json.dumps(ask_dict)
        response = requests.request(
            "POST", self.url, headers=self.headers, data=payload
        )
        return response.text


if __name__ == '__main__':
    chatTongyi = ChatTongyi("")
    result = chatTongyi.ask(test_ask)
    print(result)

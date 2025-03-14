import base64
import requests
import json

# 读取本地 图片转base64
def read_image(image_path):
    with open(image_path, "rb") as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode("utf-8")


# base64_image = read_image('test.png')
base64_image = read_image('20241111-165215.jpg')
dataImage = f"data:image/jpeg;base64,{base64_image}"
# 问题
test_ask = {
    "input": {
        "messages": [
            {
                "role": "user",
                "content": [
                    # {
                    #     "image": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"
                    # },
                    # {
                    #     "image": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/tiger.png"
                    # },
                    {
                        "image": dataImage,
                    },
                    {"text": "#对当前图片做ocr处理和翻译成中文,以json格式返回每一段的位置 css颜色 和文字"},
                ],
            }
        ]
    }
}


class ChatTongyiVl:
    token: str
    url: str

    def __init__(self, API_KEY) -> None:
        # zhipu
        self.url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        # head
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        }

    def ask(self, ask_dict: dict):
        ask_dict["model"] = "qwen-vl-max-latest"
        payload = json.dumps(ask_dict)
        response = requests.request(
            "POST", self.url, headers=self.headers, data=payload
        )
        return response.text


if __name__ == '__main__':
    chatTongyiVl = ChatTongyiVl("")
    result = chatTongyiVl.ask(test_ask)
    print(result)

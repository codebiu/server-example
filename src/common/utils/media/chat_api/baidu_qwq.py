import requests
import json

# 问题
test_ask = {
    "messages": [
        {
            "role": "user",
            "content": '以json格式{"相似度":number}返回(晾衣服去111)和(去晾衣服111)两个命令相似度数值范围0-1,只返回json,删除多余话语',
        }
    ]
}


class ChatBaidu:
    token: str
    url: str

    def __init__(self, API_KEY, SECRET_KEY) -> None:
        self.url = "https://qianfan.baidubce.com/v2/chat/completions"
        # head
        self.headers = {
            'Content-Type': 'application/json',
            'appid': API_KEY,
            'Authorization': 'Bearer ' + SECRET_KEY
        }

    def ask(self, ask_dict):
        ask_dict["model"] = "qwq-32b"
        ask_dict["web_search"] = {
            "enable": False,
            "enable_citation": False,
            "enable_trace": False
        }
        payload = json.dumps(ask_dict)
        response = requests.request(
            "POST", self.url, headers=self.headers, data=payload.encode("utf-8")
        )
        return response.text

    def ask_stream(self, ask_dict):
        ask_dict["model"] = "qwq-32b"
        ask_dict["web_search"] = {
            "enable": False,
            "enable_citation": False,
            "enable_trace": False
        }
        ask_dict["stream"] = True
        payload = json.dumps(ask_dict)

        # 发起流式请求
        response = requests.post(
            self.url, headers=self.headers, data=payload, stream=True
        )

        # 逐块读取响应内容
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                yield chunk.decode("utf-8")


if __name__ == '__main__':
    # self
    from config.index import conf
    api_key = conf["ai"]["baidu_ai_qwq"]['api_key']
    secret_key = conf["ai"]["baidu_ai_qwq"]['secret_key']
    chatBaidu = ChatBaidu(api_key, secret_key)

    # 普通请求
    # result = chatBaidu.ask(test_ask)
    # print("普通请求结果:", result)

    # 流式请求
    print("流式请求结果:")
    for chunk in chatBaidu.ask_stream(test_ask):
        print(chunk)
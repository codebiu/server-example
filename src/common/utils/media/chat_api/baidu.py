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
        # 百度
        params = {
            "grant_type": "client_credentials",
            "client_id": API_KEY,
            "client_secret": SECRET_KEY,
        }
        # 使用 AK，SK 生成鉴权签名（Access Token） access_token，或是None(如果错误)
        token_url = "https://aip.baidubce.com/oauth/2.0/token"
        self.token = str(
            requests.post(token_url, params=params).json().get("access_token")
        )
        self.url = (
            "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-speed-128k?access_token="
            + self.token
        )

        # head
        self.headers = {"Content-Type": "application/json"}

    def ask(self, ask_dict):
        payload = json.dumps(ask_dict)
        response = requests.request(
            "POST", self.url, headers=self.headers, data=payload
        )
        return response.text


if __name__ == '__main__':
    # self
    from config.index import conf
    api_key = conf["ai"]["baidu_ai"]['api_key']
    secret_key = conf["ai"]["baidu_ai"]['secret_key']
    chatBaidu = ChatBaidu(api_key, secret_key)
    result = chatBaidu.ask(test_ask)
    print(result)

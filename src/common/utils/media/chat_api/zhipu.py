import requests
import json

# 问题
test_ask = {
    "messages": [
        {
            "role": "user",
            "content": '以下数组中信息，请帮我提取出地址部分，并返回一个数组，格式为[{"name":"xxx","name":"xxx"}],只返回数组不加描述.数组:["江苏省宿迁市宿城区洋河镇酒家南路372号李小姐全球购","上海市上海市青浦区华新镇新府中路与华强街交界口三友星墅305号101室","江苏省南京市江宁区横溪街道陶吴桃盛路小姐姐","广东省中山市石岐街道街道孙文东路半山翠院6栋7-1","陕西省西安市碑林区明湖路西安交通大学到了给我打电话不打电话拒收","广西壮族自治区柳州市青秀区南宁市青秀区津头街道民族大道168号中防翡翠园A10栋"]'
        }
    ]
}




 
class ChatZhipu:
    token: str
    url: str

    def __init__(self, API_KEY) -> None:
        # zhipu
        self.url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        # head
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": API_KEY,
        }

    def ask(self, ask_dict: dict):
        ask_dict["model"] = "glm-4"
        payload = json.dumps(ask_dict)
        response = requests.request(
            "POST", self.url, headers=self.headers, data=payload
        )
        return response.text


if __name__ == '__main__':
    from config.index import conf
    api_key = conf["ai"]["zhipu"]["api_key"]
    chatZhipu = ChatZhipu(api_key)
    result = chatZhipu.ask(test_ask)
    print(result)

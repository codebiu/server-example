import requests
import pandas as pd
from bs4 import BeautifulSoup
 
header = {
    'accept': 'application/json',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/json;charset=UTF-8',
    'cookie': 'MKT_CKID=1730292097710.vfe09.t0j5; GUID=09031067118870597256; _RF1=58.20.33.185; _RSG=4oa3uKRszKEoheoV0XxD9A; _RDG=288a7d6c60cccb26a132310ea7062d44d5; _RGUID=e53dd9b5-380e-4c84-a24d-ee101fca8af2; _bfaStatusPVSend=1; _bfa=1.1730292107919.48jemx.1.1730511239226.1730511263081.4.2.101021; _ubtstatus=%7B%22vid%22%3A%221730292107919.48jemx%22%2C%22sid%22%3A4%2C%22pvid%22%3A2%2C%22pid%22%3A101021%7D; _jzqco=%7C%7C%7C%7C1730459716543%7C1.1303622818.1730292097712.1730511238884.1730511263120.1730511238884.1730511263120.0.0.0.53.53; _bfi=p1%3D101021%26p2%3D101021%26v1%3D2%26v2%3D1; _bfaStatus=success',
    'origin': 'https://flights.ctrip.com',
    'priority': 'u=1, i',
    'referer': 'https://flights.ctrip.com/schedule/csx.bjs.html?pageno=2',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
}
url1 = 'https://flights.ctrip.com/schedule/'
req = requests.get(url=url1,headers=header).text
soup = BeautifulSoup(req,'html.parser')
ac = []
for i in soup.select('ul[id="list"] li div a'):
    url2 = 'https://flights.ctrip.com'+i.get('href')
    req2 = requests.get(url=url2,headers=header).text
    soup = BeautifulSoup(req2,'html.parser')
    for i in soup.select('ul[id="ulD_Domestic"] li div a'):
        ks,js = i.get('href').replace('/schedule/','').replace('.html','').split('.')
        curl = 'https://flights.ctrip.com/schedule/getScheduleByCityPair'
        data = {"departureCityCode": f'{str(ks).upper()}', "arriveCityCode": f'{str(js).upper()}', "pageNo": 1}
        req = requests.post(url=curl,headers=header,json=data).json()
        max_page = req['totalPage']
        ac.extend(req['scheduleVOList'])
        for i in range(2,max_page+1):
            ac.extend(req['scheduleVOList'])
df = pd.DataFrame(ac)
acc = pd.DataFrame(df.pop('currentWeekSchedule').tolist())
ps = pd.concat([df,acc],axis=1)
ps.to_csv('飞机票数据.csv',index=False)
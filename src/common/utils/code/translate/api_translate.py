import hashlib
import random
import aiohttp
import asyncio


class Translator:
    """
    翻译器类，支持百度翻译和有道翻译API

    Attributes:
        source_lang (str): 源语言代码，默认'auto'表示自动检测
        target_lang (str): 目标语言代码，默认'zh'表示中文
    """

    def __init__(self, source_lang="auto", target_lang="zh"):
        """
        初始化翻译器实例

        Args:
            source_lang (str, optional): 源语言代码. Defaults to "auto".
            target_lang (str, optional): 目标语言代码. Defaults to "zh".
        """
        self.source_lang = source_lang
        self.target_lang = target_lang

    async def baidu_translate(
        self,
        query: str,
        appid: str,
        secretKey: str,
        url="https://fanyi-api.baidu.com/api/trans/vip/translate",
    ) -> dict:
        """
        使用百度翻译API进行翻译

        Args:
            query (str): 要翻译的文本
            appid (str): 百度翻译API的应用ID
            secretKey (str): 百度翻译API的密钥
            url (str, optional): 百度翻译API的URL. Defaults to "https://fanyi-api.baidu.com/api/trans/vip/translate".

        Returns:
            dict: 包含翻译结果的字典
        """

        salt = random.randint(32768, 65536)
        sign_str = f'{str(appid)}{str(query)}{str(salt)}{str(secretKey)}'
        sign = hashlib.md5(sign_str.encode()).hexdigest()

        params = {
            "q": query,
            "from": self.source_lang,
            "to": self.target_lang,
            "appid": appid,
            "salt": salt,
            "sign": sign,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

    async def tengxun_translate(
        self, query: str, appKey: str, secret: str, url="https://openapi.youdao.com/api"
    ) -> dict:
        """
        使用tengxun进行翻译
        """
        pass
    
    async def ai_translate(
        self, query: str, appKey: str, secret: str, url="https://openapi.youdao.com/api"
    ) -> dict:
        """
        使用ai进行翻译
        """
        pass


if __name__ == "__main__":
    from config.index import conf
    async def main():
        translator = Translator()
        # 百度翻译示例
        baidu_your_appid = conf["ai"]["baidufanyi"]["appid"]
        baidu_secret_key = conf["ai"]["baidufanyi"]["secret_key"]
        baidu_api_url = conf["ai"]["baidufanyi"]["api_url"]
        baidu_result = await translator.baidu_translate(
            "Hello, world!", baidu_your_appid, baidu_secret_key, baidu_api_url
        )
        print("Baidu translation:", baidu_result)

    asyncio.run(main())

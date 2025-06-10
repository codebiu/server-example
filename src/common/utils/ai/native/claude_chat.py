# import asyncio
# import boto3
# import json
# from typing import List, Dict, Optional
# from config.index import conf
# from config.log import logger
# from botocore.config import Config

# class ClaudeChat:
#     def __init__(self):
#         # 读取AI解析的配置文件
#         claude_set = conf["ai"]["Claude"]
        
#         # Claude 配置静态常量
#         self.aws_access_key_id = claude_set["bedrock"]["aws_access_key_id"]
#         self.aws_secret_access_key = claude_set["bedrock"]["aws_secret_access_key"]
#         self.region_name = claude_set["bedrock"]["region_name"]
#         self.modelId = claude_set["response"]["modelId"]
#         self.service_name = claude_set["bedrock"]["service_name"]
#         self.anthropic_version = claude_set["body"]["anthropic_version"]
        
#         # 初始化同步客户端
#         self.bedrock = boto3.client(
#             service_name=self.service_name,
#             region_name=self.region_name,
#             aws_access_key_id=self.aws_access_key_id,
#             aws_secret_access_key=self.aws_secret_access_key,
#             config=Config(
#                 read_timeout=300,
#                 connect_timeout=300
#             )
#         )
    
#     def sync_call(self, messages: List[Dict]) -> Optional[str]:
#         """
#         同步调用Claude模型
#         """
#         try:
#             body = {
#                 "anthropic_version": self.anthropic_version,
#                 "max_tokens": 10000000,
#                 "messages": messages,
#                 "temperature": 0.1
#             }
            
#             response = self.bedrock.invoke_model_with_response_stream(
#                 modelId=self.modelId,
#                 contentType='application/json',
#                 accept='application/json',
#                 body=json.dumps(body)
#             )

#             return self._process_stream_response(response)
#         except Exception as e:
#             logger.error(f"同步调用Claude模型时出错: {e}")
#             return None
    
#     async def async_call(self, messages: List[Dict]) -> Optional[str]:
#         """
#         正确的异步调用实现
#         """
#         try:
#             # 使用run_in_executor将同步调用转为异步
#             loop = asyncio.get_event_loop()
#             response = await loop.run_in_executor(
#                 None,
#                 lambda: self.bedrock.invoke_model_with_response_stream(
#                     modelId=self.modelId,
#                     contentType='application/json',
#                     accept='application/json',
#                     body=json.dumps({
#                         "anthropic_version": self.anthropic_version,
#                         "max_tokens": 10000000,
#                         "messages": messages,
#                         "temperature": 0.1
#                     })
#                 )
#             )
#             return self._process_stream_response(response)
#         except Exception as e:
#             logger.error(f"异步调用Claude模型时出错: {e}")
#             return None
    
#     def _process_stream_response(self, response) -> str:
#         """
#         处理流式响应通用方法
#         """
#         stream = response.get('body')
#         text = ""
#         if stream:
#             for event in stream:
#                 chunk = event.get('chunk')
#                 if chunk:
#                     try:
#                         chunk_json = json.loads(chunk.get('bytes').decode())
#                         if chunk_json["type"] == 'content_block_delta':
#                             text += chunk_json["delta"]["text"]
#                     except Exception as e:
#                         logger.error(f"处理流数据时出错: {e}")
#         return text
    
#     async def batch_async_call(self, messages_list: List[List[Dict]], max_concurrency: int = 5) -> List[Optional[str]]:
#         """
#         修复后的批量异步调用
#         """
#         semaphore = asyncio.Semaphore(max_concurrency)
        
#         async def limited_async_call(messages):
#             async with semaphore:
#                 return await self.async_call(messages)
        
#         tasks = [limited_async_call(messages) for messages in messages_list]
#         results = await asyncio.gather(*tasks, return_exceptions=True)
        
#         return [
#             result if not isinstance(result, Exception) else None
#             for result in results
#         ]


# if __name__ == "__main__":
#     # 测试用例
#     async def test_async_calls():
#         claude = ClaudeChat()
#         test_msg = [{"role": "user", "content": "你好，请用中文回答，1+1等于几？"}]
        
#         print("同步调用测试:")
#         print(claude.sync_call(test_msg))
        
#         print("\n异步调用测试:")
#         print(await claude.async_call(test_msg))
        
#         print("\n批量异步调用测试:")
#         batch_results = await claude.batch_async_call([test_msg]*10, max_concurrency=10)
#         for i, result in enumerate(batch_results):
#             print(f"结果 {i+1}: {result}")

#     asyncio.run(test_async_calls())
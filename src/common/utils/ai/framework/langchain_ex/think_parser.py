from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessageChunk, AIMessage
import re

class RemoveThinkTagsParser(BaseOutputParser):
    """移除所有<think></think>标签及其中间内容"""

    def parse(self, text: str) -> str:
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    async def aparse(self, text: str) -> str:
        return self.parse(text)

    def parse_result(self, result: list) -> str:
        content = result[0].content if isinstance(result, list) else result.content
        return self.parse(content)


if __name__ == "__main__":
    import asyncio
    from config.index import conf
    from config.log import logger
    from common.utils.ai.framework.do.llm_config import OllamaConfig
    from common.utils.ai.framework.ai_langchain_factory import AILangChainFactory
    async def main():
        qusetion_test = "直接回答结果数字 1+1=?"
        question_chain_prompt = "三句话描述计算{concept}的结果"
        question_chain_prompt_no_think = "三句话描述计算{concept}的结果：/no_think"
        question_chain_input = {"concept": "1+1"}
        chat_config_obj = OllamaConfig(**conf["ai.ollama.chat_model"])
        # 示例使用
        llm = await AILangChainFactory.create_llm(chat_config_obj)
        prompt = ChatPromptTemplate.from_template(question_chain_prompt)
        remove_think_tags_parser = RemoveThinkTagsParser()
        # 
        streaming_chain = (
            prompt
            | llm  # 你的模型（如 Ollama/OpenAI）
            | remove_think_tags_parser
        )
         # 1. 简单streaming_chain同步调用
        info_invoke = streaming_chain.invoke(qusetion_test)
        logger.info(f" 1. 简单streaming_chain同步调用: {info_invoke}")
        #  # 2. 简单streaming_chain异步调用
        # info_ainvoke = await streaming_chain.ainvoke(qusetion_test)
        # logger.info(f"2. 简单streaming_chain异步调用: {info_ainvoke}")
        # # 3. 异步流式调用
        # logger.info("3. 异步流式调用:")
        # async for chunk in streaming_chain.astream(question_chain_input):
        #     # logger.info(f"{chunk.content}|")
        #     logger.info(f"{chunk}|")
        # # 3. 异步非流式调用
        # info_chain_ainvoke = await streaming_chain.ainvoke(question_chain_input)
        # logger.info(f"异步非流式调用: {info_chain_ainvoke}")
    asyncio.run(main())
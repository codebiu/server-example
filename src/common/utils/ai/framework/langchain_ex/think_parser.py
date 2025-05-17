from collections.abc import Generator,AsyncGenerator
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate
import re

class RemoveThinkTagsParser(BaseOutputParser):
    """
    移除所有 <think></think> 标签及其内容的输出解析器
    
    功能说明：
    1. 移除文本中所有 <think> 开头和 </think> 结尾的标签
    2. 同时移除标签之间的全部内容
    3. 保留标签外的其他文本内容
    
    示例:
    输入: "这是正常文本<think>这是需要移除的内容</think>这是保留文本"
    输出: "这是正常文本这是保留文本"
    """
    def parse(self, text: str) -> str:
        """同步非流式解析（完整文本处理）"""
        return self._remove_tags(text)

    async def aparse(self, text: str) -> str:
        """异步非流式解析"""
        return self.parse(text)  # 直接复用同步逻辑

    def parse_stream(self, text_stream: list[str]) -> Generator:
        """同步流式解析（逐片段处理）"""
        buffer = ""
        for chunk in text_stream:
            buffer += chunk
            # 处理已确定不在标签内的内容
            clean_part, remaining = self._process_buffer(buffer)
            if clean_part:
                yield clean_part
            buffer = remaining
        # 处理最后剩余内容
        if buffer:
            yield self._remove_tags(buffer)

    async def aparse_stream(self, text_stream: list[str]) -> AsyncGenerator:
        """异步流式解析"""
        buffer = ""
        async for chunk in text_stream:
            buffer += chunk
            clean_part, remaining = self._process_buffer(buffer)
            if clean_part:
                yield clean_part
            buffer = remaining
        if buffer:
            yield self._remove_tags(buffer)

    def _remove_tags(self, text: str) -> str:
        """核心标签移除逻辑"""
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

    def _process_buffer(self, buffer: str) -> tuple[str, str]:
        """
        流式缓冲区分处理
        返回: (可安全输出的内容, 需要保留的临时内容)
        """
        open_pos = buffer.rfind('<think>')
        close_pos = buffer.rfind('</think>')

        # 情况1：没有未闭合标签
        if open_pos == -1:
            return buffer, ""

        # 情况2：有未闭合的起始标签
        if close_pos == -1 or close_pos < open_pos:
            # 返回起始标签前的内容，保留标签后内容
            return buffer[:open_pos], buffer[open_pos:]

        # 情况3：有完整标签对
        return buffer[:open_pos] + buffer[close_pos+8:], ""

    @property
    def _type(self) -> str:
        return "streaming_remove_think_tags_parser"


if __name__ == "__main__":
    import asyncio
    from config.index import conf
    from config.log import logger
    from common.utils.ai.framework.do.llm_config import OllamaConfig
    from common.utils.ai.framework.ai_langchain_factory import AILangChainFactory
    async def main():
        qusetion_test = "直接回答结果数字 1+1=?"
        question_chain_prompt = "三句话描述计算{concept}的结果"
        question_chain_prompt_no_think = "1000句话描述计算{concept}的结果：/no_think"
        question_chain_input = {"concept": "1+1"}
        chat_config_obj = OllamaConfig(**conf["ai.ollama.chat_model"])
        # 示例使用
        llm = await AILangChainFactory.create_llm(chat_config_obj)
        prompt = ChatPromptTemplate.from_template(question_chain_prompt_no_think)
        remove_think_tags_parser = RemoveThinkTagsParser()
        # 
        streaming_chain = (
            prompt
            | llm  # 你的模型（如 Ollama/OpenAI）
            # | remove_think_tags_parser
        )
         # 1. 简单streaming_chain同步调用
        # info_invoke = streaming_chain.invoke(qusetion_test)
        # logger.info(f" 1. 简单streaming_chain同步调用: {info_invoke}")
        #  # 2. 简单streaming_chain异步调用
        # info_ainvoke = await streaming_chain.ainvoke(qusetion_test)
        # logger.info(f"2. 简单streaming_chain异步调用: {info_ainvoke}")
        # 3. 异步非流式调用
        # info_chain_ainvoke = await streaming_chain.ainvoke(question_chain_input)
        # logger.info(f"异步非流式调用: {info_chain_ainvoke}")
        # 4. 异步流式调用
        logger.info("4. 异步流式调用:")
        async for chunk in streaming_chain.astream(question_chain_input):
            # logger.info(f"{chunk.content}|")
            logger.info(f"{chunk}|")
 
    asyncio.run(main())
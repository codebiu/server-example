from langchain_core.output_parsers import BaseTransformOutputParser
from langchain_core.runnables import RunnableLambda

class NoThinkTagsParser(BaseTransformOutputParser):
    """
    移除所有 <think></think> 标签及其内容的输出解析器

    功能说明：
    1. 移除content内文本中所有 <think> 开头和 </think> 结尾的标签
    2. 同时移除标签之间的全部内容
    3. 保留标签外的其他文本内容
    4. 支持同步异步流式非流式

    示例:
    输入: "这是正常文本<think>这是需要移除的内容</think>这是保留文本"
    输出: "这是正常文本这是保留文本"
    """

    def __init__(self):
        super().__init__()
        self._buffer = ""
        # think 标签外
        self._out_tag = True
    def parse(self, text):
        out_tag,in_tag = self._process_buffer(text)
        return out_tag
    def _process_buffer(self, buffer: str):
        """
        优化后的流式缓冲区分处理逻辑
        返回: (可安全输出的内容, 需要保留的临时内容)
        """
        open_pos = buffer.find("<think>")
        close_pos = buffer.rfind("</think>")

        # 情况1：当前不在标签内且没有开始标签
        if self._out_tag and open_pos == -1:
            return buffer, ""

        # 情况2：开始标签（无论是否在标签内）
        if open_pos != -1:
            # 无结束
            if close_pos == -1:
                self._out_tag = False
                return buffer[:open_pos], buffer[open_pos:]
            else:
                self._out_tag = True
                return buffer[:open_pos]+buffer[close_pos + 8:], buffer[open_pos : close_pos + 8]

        # 情况3：遇到结束标签（且当前在标签内）
        if close_pos != -1 and not self._out_tag:
            self._out_tag = True
            return buffer[close_pos + 8 :], ""
        
        # 默认情况：无标签内容
        return buffer, ""
    
# 输入
# 定义处理函数：在最后一个消息的 content 后添加 "/no_think"
def add_no_think(input_data):
    messages = input_data.copy()  # 避免直接修改原数据
    if messages and isinstance(messages[-1], dict) and "content" in messages[-1]:
        messages[-1]["content"] = f"{messages[-1]['content']} /no_think"
    return messages

# 封装为 RunnableLambda
add_no_think_runnable = RunnableLambda(add_no_think)

if __name__ == "__main__":
    import asyncio
    from config.index import conf
    from config.log import logger
    from common.utils.ai.framework.do.llm_config import OllamaConfig
    from common.utils.ai.framework.ai_langchain_factory import AILangChainFactory
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate

    async def main():
        qusetion_test = "直接回答结果数字 1+1=?"
        question_chain_prompt = "1句话描述计算{concept}的结果"
        question_chain_prompt_no_think = "1句话描述计算{concept}的结果：/no_think"
        question_chain_input = {"concept": "1+1"}
        chat_config_obj = OllamaConfig(**conf["ai.ollama.chat_model"])
        # 示例使用
        llm = AILangChainFactory.create_llm(chat_config_obj)
        prompt = ChatPromptTemplate.from_template(question_chain_prompt_no_think)
        no_think_tags_parser = NoThinkTagsParser()
        str_output_parser = StrOutputParser()
        #
        streaming_chain = (
            prompt
            | llm  # 你的模型（如 Ollama/OpenAI）
            | no_think_tags_parser
        )
        # # 1. 简单streaming_chain同步调用
        info_invoke = streaming_chain.invoke(qusetion_test)
        logger.info(f" 1. 简单streaming_chain同步调用: {info_invoke}")
        #  # 2. 简单streaming_chain异步调用
        info_ainvoke = await streaming_chain.ainvoke(qusetion_test)
        logger.info(f"2. 简单streaming_chain异步调用: {info_ainvoke}")
        # 3. 异步非流式调用
        info_chain_ainvoke = await streaming_chain.ainvoke(question_chain_input)
        logger.info(f"异步非流式调用: {info_chain_ainvoke}")
        # 4. 异步流式调用
        logger.info("4. 异步流式调用:")
        async for chunk in streaming_chain.astream(question_chain_input):
            # logger.info(f"{chunk.content}|")
            logger.info(f"{chunk}")
        # 4. 同步流式调用
        logger.info("4. 同步流式调用:")
        for chunk in streaming_chain.stream(question_chain_input):
            # logger.info(f"{chunk.content}|")
            logger.info(f"{chunk}")

    asyncio.run(main())

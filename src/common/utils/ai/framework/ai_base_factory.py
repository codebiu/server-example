from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama,OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_aws import ChatBedrock
import numpy as np

from common.utils.ai.framework.do.llm_config import (
    AWSConfig,
    ModelConfig,
    OpenAIConfig,
    OllamaConfig,
)
from common.utils.ai.framework.interface.ai_factory import AIFactory


class AILangBaseFactory(AIFactory):
    """
    AI模型工厂类，用于创建不同类型的LLM实例和嵌入模型实例
    支持Ollama、AWS Bedrock和OpenAI三种模型类型
    """

    @staticmethod
    async def create_llm(model_config: ModelConfig, streaming: bool = True) -> object:
        """
        根据配置创建对应的LLM实例

        参数:
            model_config: 模型配置对象，决定创建哪种LLM实例
            streaming: 是否启用流式响应（默认True）

        返回:
            对应的LLM实例对象

        异常:
            ValueError: 当模型类型不支持时抛出
        """
        if isinstance(model_config, OllamaConfig):
            # 创建Ollama模型实例
            return ChatOllama(model=model_config.model, base_url=model_config.url)
        elif isinstance(model_config, AWSConfig):
            # 创建AWS Bedrock模型实例
            return ChatBedrock(
                model=model_config.model,
                aws_access_key_id=model_config.aws_access_key_id,
                aws_secret_access_key=model_config.aws_secret_access_key,
                region=model_config.region_name,
                streaming=streaming,
            )
        else:
            # 默认创建OpenAI兼容模型实例
            try:
                return ChatOpenAI(
                    model=model_config.model,
                    api_key=model_config.api_key,
                    base_url=model_config.url,
                    streaming=streaming,
                )
            except Exception as e:
                raise ValueError(f"Unsupported model type: {type(model_config)}")



    @staticmethod
    async def create_embeddings(model_config: ModelConfig) -> object:
        """
        创建嵌入模型实例

        参数:
            model_config: 模型配置对象

        返回:
            对应的嵌入模型实例对象

        异常:
            ValueError: 当模型类型不支持时抛出
        """
        if isinstance(model_config, OllamaConfig):
            # 创建Ollama嵌入模型实例
            return OllamaEmbeddings(model=model_config.model, base_url=model_config.url)
        elif isinstance(model_config, AWSConfig):
            # 创建AWS Bedrock嵌入模型实例
            return ChatBedrock(
                model=model_config.model,
                aws_access_key_id=model_config.aws_access_key_id,
                aws_secret_access_key=model_config.aws_secret_access_key,
                region=model_config.region_name,
            )
        else:
            # 默认创建OpenAI兼容嵌入模型实例
            try:
                return OpenAIEmbeddings(
                    model=model_config.model,
                    api_key=model_config.api_key,
                    base_url=model_config.url,
                )
            except Exception as e:
                raise ValueError(f"Unsupported model type: {type(model_config)}")
            
    @staticmethod
    async def create_chain(
        config: ModelConfig, prompt_template: str, streaming: bool = True
    ) -> object:
        """
        创建基础LLM处理链（Prompt + LLM + Parser）
        """
        llm = await AILangBaseFactory.create_llm(config, streaming=streaming)
        prompt = ChatPromptTemplate.from_template(prompt_template)
        str_output_parser = StrOutputParser()
        return prompt | llm | str_output_parser


# 使用示例
if __name__ == "__main__":
    from config.log import logger
    import asyncio
    from config.index import conf
    from common.utils.ai.framework.llm_utils import LLMUtils
    from langchain.globals import set_debug
    # set_debug(True)
    async def main():
        # source
        qusetion_test = "直接回答结果数字 100+100=?"
        question_chain_prompt = "三句话描述计算{concept}的结果"
        question_chain_prompt_no_think = "三句话描述计算{concept}的结果：/no_think"
        question_chain_input = {"concept": "100+100"}
        answer = "200"
        # llm
        chat_config_obj = OpenAIConfig(**conf["ai.openai.chat_model_mini"])
        llm = await AILangBaseFactory.create_llm(chat_config_obj)
        streaming_chain = await AILangBaseFactory.create_chain(
            chat_config_obj,
            prompt_template=question_chain_prompt,
            streaming=True,
        )
        # 1. 简单llm同步调用
        info_invoke = llm.invoke("1+1=?")
        logger.info(f"简单llm同步调用: {info_invoke}")
        # 2. 简单llm异步调用
        info_ainvoke = await llm.ainvoke("1+1=?")
        logger.info(f"简单llm异步调用: {info_ainvoke}")
        # 3. 异步流式调用
        logger.info("异步流式调用:")
        async for chunk in streaming_chain.astream(question_chain_input):
            # logger.info(f"{chunk.content}|")
            logger.info(f"{chunk}|")
        # 3. 异步非流式调用
        info_chain_ainvoke = await streaming_chain.ainvoke(question_chain_input)
        logger.info(f"异步非流式调用: {info_chain_ainvoke}")
        
        # embedding
        embedding_config_obj = OpenAIConfig(**conf["ai.openai.embedding"])
        embeddings = await AILangBaseFactory.create_embeddings(embedding_config_obj)
        embeddings_result = await embeddings.aembed_query(qusetion_test)
        embeddings_info = LLMUtils.embeddings_info(embeddings_result)
        logger.info(f"向量模型信息: {embeddings_info}")
    # openai_config_dict = conf["ai.openai.gpt_chat_mini"]
    # ollama_qwen_config_dict = conf["ai.ollama.qwen3_4b"]
    # aws_model_config_dict = conf["ai.aws.claude_3_5"]
    
    # ollama_qwen_model_config = OllamaConfig(**ollama_qwen_config_dict)
    # aws_model_config = AWSConfig(**aws_model_config_dict)
    # # embedding
    # ollama_bge_m3_config_dict = conf["ai.ollama.bge_m3_latest"]
    # ollama_bge_m3_config = OllamaConfig(**ollama_bge_m3_config_dict)
    # openai_text_embedding_3_large_dict = conf["ai.openai.text_embedding_3_large"]
    # openai_text_embedding_3_large = OpenAIConfig(**openai_text_embedding_3_large_dict)
    # async def main():
        # model_config_use = aws_model_config
        # model_config_use = openai_text_embedding_3_large
        # # model_config_use = ollama_qwen_model_config

        # #
        # llm = await AILangBaseFactory.create_llm(model_config_use)
        # # streaming_chain = await AILangBaseFactory.create_chain(
        # #     model_config_use,
        # #     prompt_template="3步计算{concept}的结果：",
        # #     streaming=True,
        # # )

        # # 1. 简单llm同步调用
        # result = llm.invoke("1+1=?")
        # logger.info(f"简单llm同步调用: {result}")
        # # 2. 简单llm异步调用
        # result = await llm.ainvoke("1+1=?")
        # logger.info(f"简单llm异步调用: {result}")
        # # 3. 异步流式调用
        # input = {"concept": "2+2"}
        # logger.info("异步流式调用:")
        # async for chunk in streaming_chain.astream(input):
        #     logger.info(f"{chunk.content}|")
        #     # print(chunk.content, end="|", flush=True)
        # # 3. 异步非流式调用
        # input = {"concept": "langchain"}
        # info = await streaming_chain.ainvoke(input)
        # logger.info(f"异步非流式调用: {info}")
        


    asyncio.run(main())

from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

from langchain_ollama import ChatOllama,OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_aws import ChatBedrock
import numpy as np

from common.utils.ai.llm.llm_do import (
    AWSConfig,
    ModelConfig,
    OpenAIConfig,
    OllamaConfig,
)


class AILangChainFactory:
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
    async def create_chain(
        config: ModelConfig, prompt_template: str, streaming: bool = True
    ) -> object:
        """
        创建LLM处理链（Prompt + LLM）

        参数:
            config: 模型配置对象
            prompt_template: 提示模板字符串
            streaming: 是否启用流式响应

        返回:
            组合后的处理链对象（PromptTemplate | LLM）
        """
        llm = await AILangChainFactory.create_llm(config, streaming=streaming)
        prompt = ChatPromptTemplate.from_template(prompt_template)
        return prompt | llm

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


# 使用示例
if __name__ == "__main__":
    from config.log import logger
    import asyncio
    from config.index import conf
    from langchain.globals import set_debug

    # set_debug(True)
    openai_config_dict = conf["ai.openai.gpt_4o_mini"]
    ollama_qwen_config_dict = conf["ai.ollama.qwen3_4b"]
    aws_model_config_dict = conf["ai.aws.claude_3_5"]
    openai_model_config = OpenAIConfig(**openai_config_dict)
    ollama_qwen_model_config = OllamaConfig(**ollama_qwen_config_dict)
    aws_model_config = AWSConfig(**aws_model_config_dict)
    # embedding
    ollama_bge_m3_config_dict = conf["ai.ollama.bge_m3_latest"]
    ollama_bge_m3_config = OllamaConfig(**ollama_bge_m3_config_dict)
    openai_text_embedding_3_large_dict = conf["ai.openai.text_embedding_3_large"]
    openai_text_embedding_3_large = OpenAIConfig(**openai_text_embedding_3_large_dict)
    async def main():
        # model_config_use = aws_model_config
        # model_config_use = openai_text_embedding_3_large
        # # model_config_use = ollama_qwen_model_config

        # #
        # llm = await AILangChainFactory.create_llm(model_config_use)
        # # streaming_chain = await AILangChainFactory.create_chain(
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
        
        
        # model_embeddings_config_use = openai_text_embedding_3_large
        model_embeddings_config_use = ollama_bge_m3_config
        # model_config_use = ollama_qwen_model_config

        #
        embeddings = await AILangChainFactory.create_embeddings(model_embeddings_config_use)
        # streaming_chain = await AILangChainFactory.create_chain(
        #     model_config_use,
        #     prompt_template="3步计算{concept}的结果：",
        #     streaming=True,
        # )

        # 1. 简单llm同步调用 embed_documents() 和 embed_query()
        # result =embeddings.embed_query("1+1=?")
        result =await embeddings.aembed_query("1+1=?")
        logger.info(f"向量长度:{len(result)}")
        logger.info(f"向量调用: {result}")
        vector = np.array(result)  # 转换为 NumPy 数组
        norm = np.linalg.norm(vector)  # 计算 L2 范数
        logger.info(f"向量范数: {norm}")
        # 已经归一化了

    asyncio.run(main())

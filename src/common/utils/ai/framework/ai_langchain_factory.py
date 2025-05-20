# 接口类
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
# 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_aws import BedrockEmbeddings, ChatBedrock

from common.utils.ai.framework.do.llm_config import (
    AWSConfig,
    ModelConfig,
    OpenAIConfig,
    OllamaConfig,
)
from common.utils.ai.framework.interface.ai_factory import AIFactory
from common.utils.ai.framework.langchain_ex.think_parser import NoThinkTagsParser,add_no_think_runnable
# https://docsbot.ai/models/compare/gpt-4o/gpt-4-1-mini
# https://python.langchain.com/docs/concepts/

class AILangChainFactory(AIFactory):
    """
    AI模型工厂类，用于创建不同类型的LLM实例和嵌入模型实例
    支持Ollama、AWS Bedrock和OpenAI三种模型类型
    """

    @classmethod
    def create_llm(
        cls, model_config: ModelConfig, streaming: bool = True
    ) -> BaseChatModel:
        """
        根据配置创建对应的LLM实例

        parameters:
            model_config: 模型配置对象，决定创建哪种LLM实例
            streaming: 是否启用流式响应（默认True）

        returns:
            对应的LLM实例对象

        catch:
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

    @classmethod
    def create_embeddings(cls, model_config: ModelConfig) -> Embeddings:
        """
        创建嵌入模型实例

        parameters:
            model_config: 模型配置对象

        returns:
            对应的嵌入模型实例对象

        catch:
            ValueError: 当模型类型不支持时抛出
        """
        if isinstance(model_config, OllamaConfig):
            # 创建Ollama嵌入模型实例
            return OllamaEmbeddings(model=model_config.model, base_url=model_config.url)
        elif isinstance(model_config, AWSConfig):
            # 创建AWS Bedrock嵌入模型实例
            return BedrockEmbeddings(
                model_id=model_config.model,
                aws_access_key_id=model_config.aws_access_key_id,
                aws_secret_access_key=model_config.aws_secret_access_key,
                region_name=model_config.region_name,
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

    @classmethod
    def create_llm_str(
        cls,
        config: ModelConfig,
        streaming: bool = True,
    ) -> BaseChatModel:
        """
        创建基础LLM处理链（Prompt + LLM + Parser）

        parameters:
            config: 模型配置对象
            prompt_template: 提示模板字符串
            streaming: 是否启用流式响应（默认True）
            no_think: 是否启用no_think解析器（默认False 简单文本化解析器）
        """
        llm = cls.create_llm(config, streaming=streaming)
        # to_str
        if config.no_think:
            # 考虑到no_think标签解析器
            str_parser = NoThinkTagsParser()
            return add_no_think_runnable | llm | str_parser
        else:
            str_parser = StrOutputParser()
            return llm | str_parser
    
    @classmethod
    def create_chain_base(
        cls,
        config: ModelConfig,
        prompt_template: str,
        streaming: bool = True
    ) -> BaseChatModel:
        """
        创建基础LLM处理链（Prompt + LLM + Parser）

        parameters:
            config: 模型配置对象
            prompt_template: 提示模板字符串
            streaming: 是否启用流式响应（默认True）
            no_think: 是否启用no_think解析器（默认False 简单文本化解析器）
        """
        llm = cls.create_llm(config, streaming=streaming)
        
        # to_str
        str_parser = None
        if config.no_think:
            # 考虑到no_think标签解析器 qwen3
            prompt_template += " /no_think"
            str_parser = NoThinkTagsParser()
        else:
            str_parser = StrOutputParser()
        prompt = ChatPromptTemplate.from_template(prompt_template)
        return prompt | llm | str_parser


# 使用示例
if __name__ == "__main__":
    from config.log import logger
    import asyncio
    from config.index import conf
    from common.utils.ai.framework.llm_utils import LLMUtils
    from langchain.globals import set_debug

    # set_debug(True)
    async def main():
        # openai_config_dict = conf["ai.openai.chat_model_mini"]
        # ollama_qwen_config_dict = conf["ai.ollama.qwen3_4b"]
        # aws_model_config_dict = conf["ai.aws.claude_3_5"]
        # use
        chat_config_obj = OllamaConfig(**conf["ai.ollama.chat_model"])
        embedding_config_obj = OllamaConfig(**conf["ai.ollama.embedding"])
        # chat_config_obj = OpenAIConfig(**conf["ai.openai.chat_model_mini"])
        # embedding_config_obj = OpenAIConfig(**conf["ai.openai.embedding"])
        # source
        qusetion_test = "直接回答结果数字 1+1=?"
        question_chain_prompt = "根据输入回答问题:{concept}"
        question_chain_prompt_no_think = "三句话描述计算{concept}的结果：/no_think"
        question_chain_input = {"concept": "1+1"}
        answer = "2"
        if chat_config_obj:
            # llm
            # llm = AILangChainFactory.create_llm(chat_config_obj)
            llm = AILangChainFactory.create_llm_str(chat_config_obj)
            streaming_chain = AILangChainFactory.create_chain_base(
                chat_config_obj,
                # prompt_template=question_chain_prompt,
                prompt_template=question_chain_prompt,
                streaming=True,
            )
            # # 1. 简单llm同步调用
            question_chain_input = [
                {"role":"system", "content": "请错误的回答问题,结果默认加10"},
                {"role":"user", "content": "2+1=?/no_think"},
            ]
            # info_invoke = llm.invoke(question_chain_input)
            # logger.info(f"简单llm同步调用: {info_invoke}")
            # # 2. 简单llm异步调用
            info_ainvoke = await llm.ainvoke(question_chain_input)
            logger.info(f"简单llm异步调用: {info_ainvoke}")
            # # 3. 异步流式调用
            # logger.info("异步流式调用:")
            # question_chain_input = [
            #     {"role":"system", "content": "请错误的回答问题,结果默认加10"},
            #     {"role":"user", "content": "2+1=?"},
            # ]
            # async for chunk in streaming_chain.astream(question_chain_input):
            #     # logger.info(f"{chunk.content}|")
            #     logger.info(f"{chunk}|")
        #     # 3. 异步非流式调用
        #     info_chain_ainvoke = await streaming_chain.ainvoke(question_chain_input)
        #     logger.info(f"异步非流式调用: {info_chain_ainvoke}")
        # if embedding_config_obj:
        #     # embedding
        #     embeddings = AILangChainFactory.create_embeddings(
        #         embedding_config_obj
        #     )
        #     embeddings_result = await embeddings.aembed_query(qusetion_test)
        #     embeddings_info = LLMUtils.embeddings_info(embeddings_result)
        #     logger.info(f"向量模型信息: {embeddings_info}")

    asyncio.run(main())

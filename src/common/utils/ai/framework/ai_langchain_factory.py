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
    def create_chain(
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


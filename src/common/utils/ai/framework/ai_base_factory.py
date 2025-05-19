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
        pass



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
        pass
            
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
        pass

    asyncio.run(main())

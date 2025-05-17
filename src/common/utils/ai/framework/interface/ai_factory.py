from abc import ABC, abstractmethod

from common.utils.ai.framework.do.llm_config import ModelConfig

class AIFactory(ABC):
    """
    AI模型工厂类，用于创建不同类型的LLM实例和嵌入模型实例
    支持Ollama、AWS Bedrock和OpenAI三种模型类型
    """

    @abstractmethod
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
        raise NotImplementedError("子类必须实现 create_llm 方法")



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
        raise NotImplementedError("子类必须实现 create_embeddings 方法")
  

from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama  # 用于本地Qwen3
from langchain_openai import ChatOpenAI  # 用于ChatGPT

class AILangChainManager:
    """LangChain 多模型管理工具 (支持ChatGPT和本地Qwen3)"""
    
    def __init__(self, config_path: str | Path):
        """
        初始化AI管理器
        Args:
            config_path: 配置文件路径 (支持Path对象或字符串)
        """
        self.config = self._load_config(Path(config_path) if isinstance(config_path, str) else config_path)
        self.llms = {
            "chatgpt": self._init_chatgpt(),
            "qwen3": self._init_qwen3()
        }

    def _load_config(self, path: Path) -> dict:
        """加载配置文件 (使用pathlib处理路径)"""
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path.absolute()}")
        # 这里添加实际配置加载逻辑
        return {"api_key": "your_key", "ollama_host": "http://localhost:11434"}

    def _init_chatgpt(self):
        """初始化ChatGPT连接"""
        return ChatOpenAI(
            model_name="gpt-3.5-turbo",
            openai_api_key=self.config["api_key"],
            temperature=0.7
        )

    def _init_qwen3(self):
        """初始化本地Qwen3连接 (通过Ollama)"""
        return Ollama(
            base_url=self.config["ollama_host"],
            model="qwen:3b",  # 根据实际部署的Qwen版本调整
            temperature=0.5
        )

    async def generate_response(self, model_type: str, prompt: str) -> str:
        """
        生成AI响应
        Args:
            model_type: 模型类型 ('chatgpt' 或 'qwen3')
            prompt: 输入提示语
        Returns:
            AI生成的文本响应
        """
        if model_type not in self.llms:
            raise ValueError(f"不支持模型类型: {model_type}")
        
        # 使用LangChain的提示模板
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的AI助手，请用中文回答"),
            ("human", "{input}")
        ])
        
        chain = prompt_template | self.llms[model_type]
        return await chain.ainvoke({"input": prompt})

# 使用示例
if __name__ == "__main__":
    import asyncio
    from config.index import conf
    openai_config = conf["ai.openai"]

    
    
    ollama_qwen3_config = conf["ai.ollama.qwen3_4b"]
    
    async def main():
        manager = AILangChainManager()
        ai_clent= manager.create_ai_client()
        
        # ChatGPT示例
        chatgpt_response = await manager.generate_response(
            "chatgpt",
            "请解释LangChain的工作原理"
        )
        print(f"ChatGPT响应:\n{chatgpt_response}")
        
        # # 本地Qwen3示例
        # qwen_response = await manager.generate_response(
        #     "qwen3", 
        #     "如何用Python实现RAG架构?"
        # )
        # print(f"\nQwen3响应:\n{qwen_response}")
    asyncio.run(main())
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
# from langchain_community.llms import Ollama  # 用于本地Qwen3
from langchain_ollama import ChatOllama 
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from common.utils.ai.llm.llm_do import ModelConfig, OpenAIConfig, OllamaConfig


class AILangChainFactory:
    async def create_llm(model_config: ModelConfig, streaming: bool = True):
        if isinstance(model_config, OpenAIConfig):
            return ChatOpenAI(
                model=model_config.model,
                api_key=model_config.api_key,
                base_url=model_config.url,
                streaming=streaming,
            )
        if isinstance(model_config, OllamaConfig):
            return ChatOllama(
                model=model_config.model,
                base_url=model_config.url
            )
        else:
            try:
                # 创建默认llm 视为OpenAI兼容API
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
        config: ModelConfig,
        prompt_template: str,
        # streaming会自动退化非流式
        streaming: bool = True,
    ):
        llm = await AILangChainFactory.create_llm(config, streaming=streaming)
        prompt = ChatPromptTemplate.from_template(prompt_template)
        return prompt | llm


# 使用示例
if __name__ == "__main__":
    import asyncio
    from config.index import conf

    openai_config = conf["ai.openai.gpt-4o-mini"]
    # ollama_qwen_config = conf["ai.ollama.qwen3_4b"]
    ollama_qwen_config = conf["ai.ollama.qwen2_5_1_5b"]
    openai_model_config = OpenAIConfig(**openai_config)
    qwen_model_config = OllamaConfig(**ollama_qwen_config)

    async def main():
        # llm = await AILangChainFactory.create_llm(openai_model_config)
        # result = await llm.ainvoke("1+1=?")
        # print(result.content)
        # # 2. 异步流式调用
        # streaming_chain = await AILangChainFactory.create_chain(
        #     openai_model_config,
        #     prompt_template="3步计算{concept}的结果：",
        #     streaming=True,
        # )
        # input = {"concept": "2+2"}
        # async for chunk in streaming_chain.astream(input):
        #     # yield chunk.content
        #     print(chunk.content, end="|", flush=True)
        # 3. 异步非流式调用
        # streaming_chain = await AILangChainFactory.create_chain(
        #     openai_model_config,
        #     prompt_template="分步骤说明{concept}的应用场景：",
        # )
        # input = {"concept": "langchain"}
        # info = await streaming_chain.ainvoke(input)
        # print(info)
        
        
        # ollama 测试
        llm = await AILangChainFactory.create_llm(qwen_model_config)
        result = await llm.ainvoke("1+1=?")
        print(result.content)

    asyncio.run(main())

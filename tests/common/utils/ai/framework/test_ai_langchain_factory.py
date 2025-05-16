# 测试文件：D:\github\codebiu\server-example\src\common\utils\ai\framework\ai_langchain_factory.py
import pytest

from common.utils.ai.framework.ai_langchain_factory import AILangChainFactory
from common.utils.ai.llm.llm_do import (
    AWSConfig,
    ModelConfig,
    OpenAIConfig,
    OllamaConfig,
)
# 在此添加测试用例
from config.log import logger
import asyncio
from config.index import conf
from langchain.globals import set_debug

# set_debug(True)

class TestAILangChainFactory:


    @pytest.mark.asyncio
    async def test_ollama_base(self):
        config_dict = conf["ai.ollama.qwen3_4b"]
        model_use = OllamaConfig(**config_dict)
        llm = await AILangChainFactory.create_llm(model_use)
        chain = await AILangChainFactory.create_chain(
            model_use,
            prompt_template="3步计算{concept}的结果：/no_think",
            streaming=True,
        )
        # 1.简单llm同步调用
        result = llm.invoke("1+1=?")
        logger.info(f"简单llm同步调用: {result}/no_think")
        # 2. 简单llm异步调用
        result = await llm.ainvoke("1+1=?")
        logger.info(f"简单llm异步调用: {result}/no_think")
        # 3. 异步流式调用
        input = {"concept": "2+2"}
        logger.info("异步流式调用:/no_think")
        async for chunk in chain.astream(input):
            logger.info(f"{chunk.content}|")
        # 4. 异步非流式调用
        input = {"concept": "langchain"}
        info = await chain.ainvoke(input)
        logger.info(f"异步非流式调用: {info}/no_think")
        
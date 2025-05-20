# 测试文件：D:\github\codebiu\server-example\src\common\utils\ai\framework\ai_langchain_factory.py
import pytest

from common.utils.ai.framework.ai_langchain_factory import AILangChainFactory
from common.utils.ai.framework.do.llm_config import (
    AWSConfig,
    ModelConfig,
    OpenAIConfig,
    OllamaConfig,
)

# 在此添加测试用例
from common.utils.ai.framework.llm_utils import LLMUtils
from config.log import logger
import asyncio
from config.index import conf
from langchain.globals import set_debug

# 开关debug中间件
# set_debug(True)
qusetion_test = "直接回答结果数字 1+8=?"
question_chain_prompt = "2句话描述计算{concept}的结果"
question_chain_input = {"concept": "1+8"}

answer = "9"


class TestAILangChainFactory:
    async def model_try(
        chat_config_obj: ModelConfig = None,
        embedding_config_obj: ModelConfig = None,
    ):
        question_chain_prompt_use = question_chain_prompt
        qusetion_test_use = qusetion_test
        # 测试语言模型
        if chat_config_obj:
            llm = AILangChainFactory.create_llm(chat_config_obj)
            chain = AILangChainFactory.create_chain_base(
                chat_config_obj,
                prompt_template=question_chain_prompt_use,
                streaming=True
            )
            # 简单llm同步调用
            logger.info("1.简单llm异步调用:")
            info_invoke = llm.invoke(qusetion_test_use)
            logger.info(f"{info_invoke}")
            assert answer in info_invoke.content
            # 简单llm异步调用
            logger.info("2.简单llm异步调用:")
            info_ainvoke = await llm.ainvoke(qusetion_test_use)
            logger.info(f"{info_ainvoke}")
            assert answer in info_ainvoke.content
            # 异步流式调用
            logger.info("3.chain异步流式调用:")
            check_astream_ok = False
            async for chunk in chain.astream(question_chain_input):
                logger.info(f"{chunk}|")
                if answer in chunk:
                    check_astream_ok = True
            assert check_astream_ok
            # 异步非流式调用
            logger.info("4.chain异步流式调用:")
            info_chain_ainvoke = await chain.ainvoke(qusetion_test_use)
            logger.info(f"{info_chain_ainvoke}")
            assert answer in info_chain_ainvoke

        # 测试向量模型
        if embedding_config_obj:
            embeddings = AILangChainFactory.create_embeddings(
                embedding_config_obj
            )
            embeddings_result = await embeddings.aembed_query(qusetion_test_use)
            embeddings_info = LLMUtils.embeddings_info(embeddings_result)
            logger.info(f"向量模型信息: {embeddings_info}")
            assert embeddings_info is not None

    @pytest.mark.asyncio
    async def test_openai_base(self):
        # 配置
        chat_config_obj = OpenAIConfig(**conf["ai.openai.chat_model_mini"])
        # chat_config_obj = OpenAIConfig(**conf["ai.openai.chat_model"])
        embedding_config_obj = OpenAIConfig(**conf["ai.openai.embedding"])
        # 测试
        await TestAILangChainFactory.model_try(chat_config_obj, embedding_config_obj)

    @pytest.mark.asyncio
    async def test_ollama_base(self):
        # 测试
        await TestAILangChainFactory.model_try(
            OllamaConfig(**conf["ai.ollama.chat_model"]),
            OllamaConfig(**conf["ai.ollama.embedding"])
        )
        # await TestAILangChainFactory.model_try(
        #     OllamaConfig(**conf["ai.ollama.chat_model_mini"])
        # )

from config.index import conf
from common.utils.ai.framework.ai_langchain_factory import AILangChainFactory
from common.utils.ai.framework.do.llm_config import ModelConfig, LLMEX

from config.log import logger

# 配置信息
state_ai = conf["state.ai"]
if not state_ai:
    logger.info("未配置ai")
ai_configs = conf[f"ai.{state_ai}"]

# llm对象
llm_chat_mini = None
llm_chat = None
llm_embeddings = None

try:
    # 聊天 微型
    chat_mini = ai_configs["chat_mini"]
    if chat_mini:
        chat_mini_config: ModelConfig = LLMEX.get_config(chat_mini["type"], chat_mini)
        llm_chat_mini = AILangChainFactory.create_chain(chat_mini_config)
    # 聊天 基础
    chat_base = ai_configs["chat_base"]
    if chat_base:
        chat_base_config_obj: ModelConfig = LLMEX.get_config(
            chat_base["type"], chat_base
        )
        llm_chat = AILangChainFactory.create_chain(chat_base_config_obj)
    #  embeddings
    embedding_config_dict = ai_configs["embedding"]
    if embedding_config_dict:
        embedding_config_obj: ModelConfig = LLMEX.get_config(
            embedding_config_dict["type"], embedding_config_dict
        )
        llm_embeddings = AILangChainFactory.create_embeddings(embedding_config_obj)
except Exception as e:
    logger.error(f"llm初始化失败:{e}")

if __name__ == "__main__":
    result = llm_chat.invoke("你好")
    print(result)

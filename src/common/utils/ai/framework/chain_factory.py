class ChainFactory:
    def __init__(self,llm,embedding):
        self.llm = llm
        self.embedding =embedding
        
    def invoke():
        pass
    
    async def ainvoke():
        pass
    def stream():
        pass
    
    async def astream():
        pass

    # async def asplit_into_list(
    #     input: list[str],
    # ):
    #     buffer = ""
    #     async for chunk in input:
    #         buffer += chunk
    #         yield [buffer.strip()]


# 使用示例 区分think
if __name__ == "__main__":
    from config.log import logger
    import asyncio
    from config.index import conf
    from langchain.globals import set_debug


    async def main():
        pass
        # async for chunk in list_chain.astream({"animal": "bear"}):
        #     print(chunk, flush=True)

    asyncio.run(main())

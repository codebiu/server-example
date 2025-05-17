from pydantic import BaseModel, Field,field_validator
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
class ChainFactory:
    def __init__(self,llm,embedding):
        self.llm = llm
        self.embedding =embedding
        
    # def 
    
    
    def get_template_chain(self):
        # 1. 定义单个笑话的数据结构
        class Joke(BaseModel):
            setup: str = Field(description="笑话的开头问题")
            punchline: str = Field(description="笑话的结尾笑点")

            @field_validator("setup")
            def question_ends_with_question_mark(cls, field):
                if field[-1] != "?":
                    raise ValueError("问题必须以问号结尾！")
                return field

        # 2. 创建解析器，指定返回类型为 List[Joke]
        parser = PydanticOutputParser(pydantic_object=list[Joke])  # 关键修改点

        # 3. 构建提示模板
        prompt = PromptTemplate(
            template="请回答用户问题，返回指定格式的JSON数据。\n{format_instructions}\n问题：{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.llm | parser
        return chain

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

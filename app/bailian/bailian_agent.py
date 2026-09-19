# -*- coding: utf-8 -*-
"""
@Time : 2026/9/18 15:53
@Author: janic
@File: bailian_agent.py
"""
from langchain.agents import create_agent
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_experimental.utilities import PythonREPL

from app.bailian.common import create_calc_tools, llm, chat_prompt_template


class Output(BaseModel):
    args: str = Field("工具的入参")
    result: str = Field("计算的结果")
    think: str = Field("思考过程")


parser = JsonOutputParser(pydantic_object=Output)
format_instruction = parser.get_format_instructions()
# print(format_instruction)
llm_with_tools = llm.bind_tools(create_calc_tools())

agent = create_agent(
    tools=create_calc_tools(),
    model=llm_with_tools,
    debug=True
)

prompt = chat_prompt_template.format_messages(
    role="计算",
    domain="使用工具进行数学计算",
    question=f"""
请阅读下方的问题，并返回一个严格的JSON对象，不要使用markdown代码块包裹，
格式要求：
{format_instruction}
-----
问题：100+252=？
"""
)

resp = agent.invoke({"messages": prompt})
print(resp['messages'][-1].content)
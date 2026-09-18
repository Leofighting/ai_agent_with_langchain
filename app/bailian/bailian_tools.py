# -*- coding: utf-8 -*-
"""
@Time : 2026/9/18 14:47
@Author: janic
@File: bailian_tools.py
"""
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.bailian.common import chat_prompt_template, llm


class AddInputArgs(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

@tool(
    args_schema=AddInputArgs
)
def add(a, b):
    """add two numbers"""
    return a + b


# add_tools = Tool(
#     func=add,
#     name="add",
#     description="add two numbers",
# )
tool_dict = {
    "add": add
}
llm_with_tools = llm.bind_tools([add])

chain = chat_prompt_template | llm_with_tools

resp = chain.invoke(input={"role": "计算", "domain": "数学计算", "question": "使用工具计算：99+63=?"})
# print(resp)

for tool_calls in resp.tool_calls:
    print(tool_calls)
    print("*"*88)
    args = tool_calls['args']
    print(args)
    print("*" * 88)
    func_name = tool_calls["name"]
    print(func_name)
    print("*" * 88)
    tool_func = tool_dict[func_name]
    tool_content = tool_func.invoke(args)
    print(tool_content)

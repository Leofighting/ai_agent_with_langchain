# -*- coding: utf-8 -*-
"""
@Time : 2026/9/18 14:47
@Author: janic
@File: common.py
"""
import os
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate, ChatMessagePromptTemplate, FewShotPromptTemplate, PromptTemplate

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

llm = ChatOpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen3.8-27b",
    api_key=DASHSCOPE_API_KEY,
    streaming=True
)

system_message_prompt_template = ChatMessagePromptTemplate.from_template(
    template="你是一位{role}专家，擅长回答{domain}领域的问题",
    role="system"
)

human_message_prompt_template = ChatMessagePromptTemplate.from_template(
    template="用户问题：{question}",
    role="user"
)

chat_prompt_template = ChatPromptTemplate.from_messages(
    [
        system_message_prompt_template,
        human_message_prompt_template
    ]
)

class AddInputArgs(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

@tool(
    args_schema=AddInputArgs,
    return_direct=False
)
def add(a, b):
    """add two numbers"""
    return a + b


def create_calc_tools():
    return [add]


calc_tools = create_calc_tools()

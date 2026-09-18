# -*- coding: utf-8 -*-
"""
@Time : 2026/9/18 14:47
@Author: janic
@File: common.py
"""
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from langchain_core.prompts import ChatPromptTemplate, ChatMessagePromptTemplate, FewShotPromptTemplate, PromptTemplate

llm = ChatOpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen3.8-27b",
    api_key=SecretStr("sk-6e4fc0d032094cd8ae8aa084bb75923d"),
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
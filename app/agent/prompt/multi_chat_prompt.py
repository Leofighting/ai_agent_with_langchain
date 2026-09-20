# -*- coding: utf-8 -*-
"""
@Time : 2026/9/20 11:13
@Author: janic
@File: multi_chat_prompt.py
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

multi_chat_prompt = ChatPromptTemplate(
    [
        ("system", "你是以为优秀的技术专家，擅长解决各种开发中的技术问题"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ]
)
# -*- coding: utf-8 -*-
"""
@Time : 2026/9/20 11:11
@Author: janic
@File: qwen.py
"""
import os

from langchain_openai import ChatOpenAI

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

llm_qwen = ChatOpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen3.8-27b",
    api_key=DASHSCOPE_API_KEY,
    streaming=True
)
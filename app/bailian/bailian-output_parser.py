# -*- coding: utf-8 -*-
"""
@Time : 2026/9/18 17:21
@Author: janic
@File: bailian-output_parser.py
"""
from langchain_core.output_parsers import StrOutputParser

from app.bailian.common import chat_prompt_template, llm

parser = StrOutputParser()
chain = chat_prompt_template | llm | parser

resp = chain.invoke(input={
    "role": "计算",
    "domain": "数学计算",
    "question": "100+444"
})

print(resp)

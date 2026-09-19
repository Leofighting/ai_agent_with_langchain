# -*- coding: utf-8 -*-
"""
@Time : 2026/9/18 11:42
@Author: janic
@File: bailian_prompt.py
"""
from sys import prefix

from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langchain_core.prompts import ChatPromptTemplate, ChatMessagePromptTemplate, FewShotPromptTemplate, PromptTemplate
from torch.utils.flop_counter import suffixes

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
prompt = chat_prompt_template.format_messages(
    role="编程",
    domain="python",
    question="写一个冒泡排序")

# resp = llm.stream(prompt)
#
# for chunk in resp:
#     print(chunk.content, end="")

example_template = "输入：{input} \n输出“{output}"
examples = [
    {"input": "将'Hello'翻译成中文", "output": "你好"},
    {"input": "将'Goodbye'翻译成中文", "output": "再见"}
]

few_shot_prompt_template = FewShotPromptTemplate(
    examples=examples,
    example_prompt=PromptTemplate.from_template(example_template),
    prefix="请将以下英文内容翻译成中文：",
    suffix="输入：{text} \n输出：",
    input_variables=["text"]
)

# print(few_shot_prompt_template)
prompt1 = few_shot_prompt_template.format(text="""
if you're between 25 and 32 years old, read this carefully.
your body will never be as recoverable as it is right now.
""")

# resp = llm.stream(prompt1)

chain = few_shot_prompt_template | llm

resp = chain.stream(input={"text": """if you're between 25 and 32 years old, read this carefully.
your body will never be as recoverable as it is right now."""})

for chunk in resp:
    print(chunk.content, end="")


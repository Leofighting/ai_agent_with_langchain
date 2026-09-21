# -*- coding: utf-8 -*-
"""
@Time : 2026/9/21 7:47
@Author: janic
@File: agent_chat.py
"""
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent
from langgraph.checkpoint.redis import RedisSaver

from app.agent.model.qwen import llm_qwen
from app.agent.tools.file_tools import file_tools


def create_agent_():
    # memory = MemorySaver()
    with RedisSaver.from_conn_string("redis://127.0.0.1:6379") as memory:
        memory.setup()
        agent = create_agent(
            model=llm_qwen,
            tools=file_tools,
            checkpointer=memory,
            debug=True
        )
        return agent


def run_agent():
    config = RunnableConfig(configurable={"thread_id": 1})
    agent = create_agent_()
    res = agent.invoke(input={"messages": [("user", "我们刚才聊了什么")]}, config=config)
    print("#"*88)
    print(res)
    print("#"*88)


if __name__ == '__main__':
    run_agent()
# -*- coding: utf-8 -*-
"""
@Time : 2026/9/20 11:16
@Author: janic
@File: multi_chat.py
"""
import uuid

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory, FileChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.agent_toolkits.file_management import FileManagementToolkit
from langchain.agents import create_agent

from app.agent.model.qwen import llm_qwen
from app.agent.prompt.multi_chat_prompt import multi_chat_prompt


def get_session_history(session_id: str):
    # if session_id not in store:
    #     store[session_id] = ChatMessageHistory()
    # print(store)
    # return store[session_id]
    return FileChatMessageHistory(f"{session_id}.json")


file_toolkit = FileManagementToolkit(root_dir=r"D:\code_project\ai_agent_with_langchain\.temp")
file_tools = file_toolkit.get_tools()

# agent = create_agent(model=llm_qwen, tools=file_tools)
llm_with_tools = llm_qwen.bind_tools(tools=file_tools)

chain = multi_chat_prompt | llm_with_tools | StrOutputParser()

chain_with_history = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history",
)

chat_history = ChatMessageHistory()
chat_history.add_user_message(HumanMessage(content="我叫Leo"))

# for chunk in chain.stream({"question": "你是谁？", "chat_history": chat_history.messages}):
#     print(chunk, end="")

session_id = uuid.uuid4()

while True:
    user_input = input("用户：")
    if user_input.lower() == "exit":
        break

    response = chain_with_history.stream(
        {"question": user_input},
        config={"configurable": {"session_id": session_id}}
    )
    print("\n")
    print("助理：")
    for chunk in response:
        print(chunk, end="")
    print("\n")
    print("$"*88)

# -*- coding: utf-8 -*-
"""
@Time : 2026/9/21 15:45
@Author: janic
@File: code_agent.py
"""
import asyncio
import time

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver

from app.agent.model.qwen import llm_qwen
from app.agent.rag.rag import create_client, retrieve_index, query_rag_from_bailian
from app.agent.tools.file_saver import FileSaver
from app.agent.tools.file_tools import file_tools
from app.agent.tools.powershell_tools import get_stdio_powershell_tools
from app.agent.tools.rag_tools import get_stdio_rag_tools
from app.agent.tools.shell_tools import get_stdio_shell_tools


def format_debug_output(step_name: str, content: str, is_tool_call=False)->None:
    if is_tool_call:
        print(f"♻️【工具调用】 {step_name}")
        print("-" * 44)
        print(content.strip())
        print("-" * 44)
    else:
        print(f"💡【{step_name}】")
        print("-"*44)
        print(content.strip())
        print("-" * 44)


async def run_agent():

    memory = FileSaver()
    # memory = MemorySaver()

    shell_tools = await get_stdio_shell_tools()
    powershell_tools = await get_stdio_powershell_tools()
    rag_tools = await get_stdio_rag_tools()
    tools = file_tools + shell_tools + powershell_tools + rag_tools

    prompt = PromptTemplate.from_template(
        template="""
        # 角色
        你是一名优秀的工程师，你的名字是{name}
        # 要求
        执行任务之前，先使用 query_rag 工具查询知识库，根据知识库的知识执行任务
        """
    )

    agent = create_agent(
            model=llm_qwen,
            tools=tools,
            checkpointer=memory,
            debug=False,
            system_prompt=SystemMessage(prompt.format(name="Bot")),
        )
    config1 = RunnableConfig(configurable={"thread_id": 10}, recursion_limit=100)
    while True:
        user_input = input("用户：")
        if user_input == "exit":
            break

        print("\n🤖 助手正在思考和处理中...")
        print("="*66)

        iteration_count = 0
        start_time = time.time()
        last_tool_time = start_time

        # 方案一：从阿里云百炼知识库读取知识
        # workspace_id = ""
        # index_id = ""
        # bailian_client = create_client()
        rag = query_rag_from_bailian(user_input)
        user_prompt = f"""
        # 要求
        执行任务之前，先使用 query_rag 工具查询知识库，根据知识库中的知识执行任务
            # 相关知识
            {rag}
            
            # 用户问题
            {user_input}
            """

        async for chunk in  agent.astream(input={"messages": [("user", user_prompt)]}, config=config1):
            iteration_count += 1


            print(f"\n☀️第{iteration_count}步执行：")
            print("-"*33)
            items = chunk.items()
            for node_name, node_output in items:
                # print(f"{node_name}: {node_output}")
                if "messages" in node_output:
                    for msg in node_output["messages"]:
                        if isinstance(msg, AIMessage):
                            if msg.content:
                                format_debug_output("AI 思考：", msg.content)
                            else:
                                for tool in msg.tool_calls:
                                    format_debug_output("工具调用：", f"{tool['name']}: {tool['args']}")
                        elif isinstance(msg, ToolMessage):
                            tool_name = getattr(msg, "name", "unknown")
                            tool_content = msg.content
                            current_time = time.time()
                            tool_duration = current_time - last_tool_time
                            tool_result = f"""⚙️工具：{tool_name}
                                            📮结果：
                                            {tool_content}
                                            ✅️状态：执行完成，可以开始下一个任务
                                            ⌚️执行时间：{tool_duration:.2f} 秒
                                            """
                            format_debug_output("工具执行结果：", tool_result, is_tool_call=True)
                        else:
                            format_debug_output("未实现", f"暂未实现的打印内容：{chunk}")
        print()


if __name__ == '__main__':
    asyncio.run(run_agent())
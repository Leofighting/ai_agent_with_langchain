# -*- coding: utf-8 -*-
"""
@Time : 2026/9/20 7:30
@Author: janic
@File: mcp_playwright_client.py
"""
import asyncio

from aiohttp import ClientSession
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from mcp import StdioServerParameters, stdio_client, ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools

from app.bailian.common import llm


async def mcp_playwright_client():

    # server_params = StdioServerParameters(
    #     command="npx",
    #     args=["-y", "@executeautomation/playwright-mcp-server"]
    # )

    # 通过npx调用mcp
    """
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>"
      }
    }
    """
    server_params = StdioServerParameters(
        command="npx",
        args=[
        "-y",
        "@modelcontextprotocol/server-github"
      ],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": "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"}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            print(tools)
            agent = create_agent(model=llm, tools=tools, debug=True)
            response = await agent.ainvoke(input={"messages": [("user", "我的账号 Leofighting 有哪些代码仓库")]})
            # print(response)
            messages = response["messages"]
            for message in messages:
                if isinstance(message, HumanMessage):
                    print("用户：", message.content)
                    print("#"*88)
                elif isinstance(message, AIMessage):
                    if message.content:
                        print("AI: ", message.content)
                        print("#" * 88)
                    else:
                        for tool_call in message.tool_calls:
                            print("AI「调用工具」：", tool_call["name"], tool_call["args"])
                            print("#" * 88)
                elif isinstance(message, ToolMessage):
                    print("调用工具：", message.name)
                    print("#" * 88)


if __name__ == '__main__':
    asyncio.run(mcp_playwright_client())
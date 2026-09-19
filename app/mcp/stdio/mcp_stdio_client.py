# -*- coding: utf-8 -*-
"""
@Time : 2026/9/19 11:37
@Author: janic
@File: mcp_stdio_client.py
"""
import asyncio

from langchain.agents import create_agent
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

from app.bailian.common import llm


async def create_mcp_stdio_client():
    server_params = StdioServerParameters(
        command="python",
        args=[r"D:\code_project\ai_agent_with_langchain\app\mcp\stdio\mcp_stdio_server.py"]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            # print(tools)
            agent = create_agent(model=llm,
                                 tools=tools,
                                 debug=True,)
            resp = await agent.ainvoke({"messages": "1+5*2=?"})
            return resp



if __name__ == '__main__':
    asyncio.run(create_mcp_stdio_client())

# -*- coding: utf-8 -*-
"""
@Time : 2026/9/19 10:44
@Author: janic
@File: amap_mcp_client.py
"""
import asyncio

from langchain.agents import create_agent
from langchain_core.prompts import PromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient

from app.bailian.common import llm, file_tools
from settings import GAODE_KEY


async def create_amap_mcp_client():
    mcp_config = {
      "amap": {
          "url": f"https://mcp.amap.com/sse?key={GAODE_KEY}",
          "transport": "sse"
      }
    }
    client = MultiServerMCPClient(mcp_config)
    # print(client)
    tools = await client.get_tools()
    return client, tools


async def create_and_run_agent():
    client, tools = await create_amap_mcp_client()
    agent = create_agent(
        model=llm,
        tools=tools+file_tools,
        debug=True
    )
    prompt_template = PromptTemplate.from_template("你是一个智能助手，可以调用高德mcp工具。\n\n问题：{input_}")
    prompt = prompt_template.format(input_=r"""
    目标：
    - 今天下午14:00，我要从顺德区勒流街道光大小学到顺峰山，
    - 要考虑出行时间的拥堵情况，以及重点周边的停车情况
    - 输出一个html页面
    要求：
    - 制作一个网页来显示出行的路线和拥堵情况、停车说明，输出一个html页面，保存在 "D:\code_project\ai_agent_with_langchain\.temp" 目录中
    - 网页使用简约美观的页面风格，以及卡片展示
    - 行程规划的结果，要能够在高德APP中展示，并集成到H5页面中
    """)
    return await agent.ainvoke({"messages": prompt})



if __name__ == '__main__':
    asyncio.run(create_and_run_agent())
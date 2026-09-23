# -*- coding: utf-8 -*-
"""
@Time : 2026/9/21 15:37
@Author: janic
@File: shell_tools.py
"""
import asyncio
import os

from app.agent.utils.mcp import create_mcp_stdio_client


async def get_stdio_rag_tools():
    params = {
        "command": "python",
        "args": [
            r"D:\code_project\ai_agent_with_langchain\app\agent\rag\rag.py"
        ],
        # "env": {
        #     **os.environ,
        #     "PYTHONUTF8": "1",
        #     "PYTHONIOENCODING": "utf-8",
        # },
        # # 关键 2：告诉 MCP 客户端按 UTF-8 解码，遇到坏字节不崩
        # "encoding": "utf-8",
        # "encoding_error_handler": "replace",
    }
    client, tools = await  create_mcp_stdio_client("rag_tools", params)
    return tools


if __name__ == '__main__':
    tool = asyncio.run(get_stdio_rag_tools())
    # print(tool)
# -*- coding: utf-8 -*-
"""
@Time : 2026/9/21 15:37
@Author: janic
@File: mcp.py
"""
from langchain_mcp_adapters.client import MultiServerMCPClient


async def create_mcp_stdio_client(name, params):
    config = {
        name: {
            "transport": "stdio",
            # "command": params["command"],
            # "args": params["args"],
            # "env": params.get("env"),
            # "encoding": params.get("encoding", "utf-8"),
            # "encoding_error_handler": params.get("encoding_error_handler", "strict"),
            **params
        }
    }

    print(config)
    client = MultiServerMCPClient(config)

    tools = await client.get_tools()
    return client, tools
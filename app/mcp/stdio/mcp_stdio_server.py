# -*- coding: utf-8 -*-
"""
@Time : 2026/9/19 11:33
@Author: janic
@File: mcp_stdio_server.py
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math Tools")


@mcp.tool()
def add(a:int, b:int)->int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int)->int:
    """Multiply two numbers"""
    return a * b


if __name__ == '__main__':
    mcp.run(transport="stdio")
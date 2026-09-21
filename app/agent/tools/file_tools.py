# -*- coding: utf-8 -*-
"""
@Time : 2026/9/21 7:48
@Author: janic
@File: file_tools.py
"""
from langchain_community.agent_toolkits.file_management import FileManagementToolkit

file_tools = FileManagementToolkit(
    root_dir=r"D:\code_project\ai_agent_with_langchain\.temp").get_tools()

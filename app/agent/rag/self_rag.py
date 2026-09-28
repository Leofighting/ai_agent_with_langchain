# -*- coding: utf-8 -*-
"""
@Time : 2026/9/23 17:58
@Author: janic
@File: self_rag.py
"""
import sys
from typing import Annotated

from mcp.server import FastMCP
from pydantic import Field

from app.agent.rag.rag import create_client, retrieve_index, upload_rag_file_to_bailian
from settings import BAILIAN_WORKSPACE_ID, INDEX_ID

mcp = FastMCP()

@mcp.tool(
    name="query_rag_from_bailian",
    description="从百炼知识库中查询信息"
)
def query_rag_from_bailian(query: Annotated[str, Field(description="访问知识库查询的内容",
                                     examples=["终端的规范"])])->str:
    bailian_client = create_client()
    workspace_id1 = BAILIAN_WORKSPACE_ID
    index_id1 = INDEX_ID
    rag = retrieve_index(bailian_client, workspace_id1, index_id1, query)
    result = ""
    for data in rag.body.data.nodes:
        result += f"\n{data.text}\n"
        sys.stderr.write("-" * 66 + "\n")
        sys.stderr.write(f"[query_rag_from_bailian] Query: {query}\n")
        sys.stderr.write(f"Result: {result}\n")
        sys.stderr.write("-" * 66 + "\n")
        return result


@mcp.tool(name="upload_rag_from_local_file_path", description="将本地的知识文件上传到百炼平台知识库")
def upload_rag_to_bailian(
        file_path: Annotated[str, Field(description="本地知识文件的路径，需要传入绝对路径",
                                        examples=[r"D:\code_project\ai_agent_with_langchain\app\agent\rag\terminal.txt"])])->str:
    file_id = upload_rag_file_to_bailian()




if __name__ == '__main__':
    # bailian_client1 = create_client()
    # print(bailian_client1)
    # workspace_id1 = BAILIAN_WORKSPACE_ID
    # index_id1 = INDEX_ID
    # print(ALIBABA_CLOUD_ACCESS_KEY_ID)
    # print(ALIBABA_CLOUD_ACCESS_KEY_SECRET)
    # res = retrieve_index(bailian_client1, workspace_id1, index_id1, query="终端的操作规范是什么")
    # print(res.body)
    mcp.run(transport="stdio")
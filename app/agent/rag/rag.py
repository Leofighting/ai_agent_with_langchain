# -*- coding: utf-8 -*-
"""
@Time : 2026/9/22 16:11
@Author: janic
@File: rag.py
"""
import os
import sys
from typing import Annotated

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import alibabacloud_bailian20231229.client as bailian_client
from alibabacloud_bailian20231229 import models as bailian_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as tea_models
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from settings import BAILIAN_WORKSPACE_ID, INDEX_ID

load_dotenv()

mcp = FastMCP()


def create_client()->bailian_client.Client:
    config = open_api_models.Config(
        access_key_id=os.environ["ACCESSKET_ID"],
        access_key_secret=os.environ["ACCESSKET_SECRET"],
    )

    config.endpoint = 'bailian.cn-beijing.aliyuncs.com'
    # config.endpoint = "llm-kirz0c1163fip4c8.cn-beijing.maas.aliyuncs.com"
    return bailian_client.Client(config)


def retrieve_index(client, workspace_id, index_id, query):
    retrieve_request = bailian_models.RetrieveRequest(
        index_id=index_id,
        query=query,
    )
    runtime = tea_models.RuntimeOptions()
    return client.retrieve_with_options(
        workspace_id=workspace_id,
        tmp_req=retrieve_request,
        headers={},
        runtime=runtime,
    )


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
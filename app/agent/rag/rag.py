# -*- coding: utf-8 -*-
"""
@Time : 2026/9/22 16:11
@Author: janic
@File: rag.py
"""
import os
import sys
from typing import Annotated
import hashlib

import requests
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


def calculate_md5(file_path: str)->str:
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda : f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def apply_lease(client, category_id, file_name, file_md5, file_size, workspace_id):
    headers = {}
    runtime = tea_models.RuntimeOptions()
    request = bailian_models.ApplyFileUploadLeaseRequest(
        file_name=file_name,
        md_5=file_md5,
        size_in_bytes=file_size,
    )
    return client.apply_file_upload_lease(
        category_id,
        workspace_id,
        request,
        headers,
        runtime
    )


def get_file_info(file_path):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    file_md5 = calculate_md5(file_path)
    return file_name, file_size, file_md5


def apply_lease_by_file_path(client, category_id, workspace_id, file_path):
    file_name, file_size, file_md5 = get_file_info(file_path)
    return apply_lease(client, category_id, file_name, file_md5, file_size, workspace_id)


def upload_file_to_bailian(upload_url, headers, file_path):
    with open(file_path, "rb") as f:
        file_content = f.read()

    upload_headers = {
        "Content-Type": headers["Content-Type"],
        "X-bailian-extra": headers["X-bailian-extra"],
    }
    response = requests.put(upload_url, data=file_content, headers=upload_headers)
    response.raise_for_status()


def add_file_to_bailian_category(client, lease_id, parser, category_id, workspace_id):
    headers = {}
    runtime = tea_models.RuntimeOptions()

    request = bailian_models.AddFileRequest(
        lease_id=lease_id,
        parser=parser,
        category_id=category_id,
    )

    return client.add_file_with_options(workspace_id, request, headers, runtime)


def describe_file(client, workspace_id, file_id):
    headers = {}
    runtime = tea_models.RuntimeOptions()
    return client.describe_file_with_options(workspace_id, file_id, headers, runtime)


def create_index(client, workspace_id, name, file_id, structure_type="unstructured", source_type="DATA_CENTER_FILE", sink_type="BUILT_IN"):
    headers = {}
    runtime = tea_models.RuntimeOptions()
    request = bailian_models.CreateIndexRequest(
        structure_type=structure_type,
        source_type=source_type,
        sink_type=sink_type,
        name=name,
        document_ids=[file_id]
    )

    return client.create_index_with_options(workspace_id, request, headers, runtime)


def submit_index(client, workspace_id, index_id):
    headers = {}
    runtime = tea_models.RuntimeOptions()
    submit_index_job_request = bailian_models.SubmitIndexJobRequest(index_id=index_id)
    return client.submit_index_job_with_options(workspace_id, submit_index_job_request, headers, runtime)


def get_index_job_status(client, workspace_id, index_id, job_id):
    headers = {}
    runtime = tea_models.RuntimeOptions()
    get_index_job_status_request = bailian_models.GetIndexJobStatusRequest(
        index_id=index_id,
        job_id=job_id
    )

    return client.get_index_job_status_with_options(workspace_id, get_index_job_status_request, headers, runtime)


def list_indices(client, workspace_id):
    headers = {}
    runtime = tea_models.RuntimeOptions()
    list_indices_request = bailian_models.ListIndicesRequest()
    return client.list_indices_with_options(workspace_id, list_indices_request, runtime, headers)


def submit_index_add_documents_job(client, workspace_id, index_id, file_id, source_type="DATA_CENTER_FILE"):
    headers = {}
    runtime = tea_models.RuntimeOptions()
    submit_index_add_documents_job_request = bailian_models.SubmitIndexAddDocumentsJobRequest(
        index_id=index_id,
        document_ids=[file_id],
        source_type=source_type
    )
    return client.submit_index_add_documents_job_with_options(workspace_id, submit_index_add_documents_job_request, headers, runtime)


def add_document_to_index(client, workspace_id, index_id, file_id):
    job_response = submit_index_add_documents_job(client, workspace_id, index_id, file_id)
    job_id = job_response.body.data.id
    job_status = get_index_job_status(client, workspace_id, index_id, job_id)
    return job_status.body.data


def upload_rag_file_to_bailian(client, workspace_id, category_id, file_path):
    lease = apply_lease_by_file_path(client, category_id, workspace_id, file_path)
    headers = lease.body.data.param.headers
    lease_id = lease.body.data.file_upload_lease_id
    upload_url = lease.body.data.param.url
    print("文件租约申请成功")

    upload_file_to_bailian(upload_url, headers, file_path)

    add_file_response = add_file_to_bailian_category(client,
                                                     lease_id,
                                                     "DASHSCOPE_DOCMIND",
                                                     category_id,
                                                     workspace_id)
    file_id = add_file_response.body.data.file_id
    print("添加分类成功")

    describe_file_response = describe_file(client, workspace_id, file_id)
    print("文件上传状态")

    return describe_file_response




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
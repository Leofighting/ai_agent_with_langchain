# -*- coding: utf-8 -*-
"""
@Time : 2026/9/27 15:54
@Author: janic
@File: vm_tools.py
"""
import os.path
import shlex
import subprocess
import tempfile
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP()


def run_limavm_shell_command(command: Annotated[str, Field(description="shell command will be executed",
                                                    examples=["ls -al"])]) -> str:
    try:
        wrapper_command = "limactl shell lima-test " + command
        shell_command = shlex.split(wrapper_command)
        if "rm" in shell_command:
            raise Exception("不允许使用rm")
        res = subprocess.run(shell_command, shell=False, capture_output=True, text=True)
        if res.returncode != 0:
            return res.stderr
        return res.stdout
    except Exception as e:
        return str(e)


def run_limavm_command(command: Annotated[str, Field(description="shell command will be executed",
                                                    examples=["ls -al"])]) -> str:
    try:
        wrapper_command = "limactl " + command
        shell_command = shlex.split(wrapper_command)
        if "rm" in shell_command:
            raise Exception("不允许使用rm")
        res = subprocess.run(shell_command, shell=False, capture_output=True, text=True)
        if res.returncode != 0:
            return res.stderr
        return res.stdout
    except Exception as e:
        return str(e)


@mcp.tool(name="make_dir_in_vm", description="在指定的虚拟机中创建目录，相当于 mkdir -p 命令")
def make_dir_in_vm(dir_path: Annotated[str, Field(description="要创建的目录路径", examples=[r"D:\code_project\ai_agent_with_langchain\.temp"])]):
    res = run_limavm_shell_command("mkdir -p " + dir_path)
    return res


@mcp.tool(name="list_files_in_vm", description="查看虚拟机中指定目录，相当于 ls -al 命令")
def list_files_in_vm(dir_path: Annotated[str, Field(description="要查看的目录路径", examples=[r"D:\code_project\ai_agent_with_langchain\.temp"])]):
    return run_limavm_shell_command("ls -al " + dir_path)


@mcp.tool(name="write_file_to_vm", description="向虚拟机中写入指定文件")
def write_file_to_vm(file_path: Annotated[str, Field(description="写入虚拟机中的文件地址", examples=[r"D:\code_project\ai_agent_with_langchain\.temp"])],
                     content: Annotated[str, Field(description="写入虚拟机中的文件内容", examples=["hello"])]):
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    run_limavm_command(f"""copy {tmp_file_path} lima-test:{file_path}""")
    change_file_permission_in_vm(file_path, "755")


def change_file_permission_in_vm(file_path, mode):
    return run_limavm_shell_command(f"chmod {mode} {file_path}")


@mcp.tool(name="upload_directory_to_vm", description="将本地文件目录上传至虚拟机指定目录")
def upload_directory_to_vm(
        local_dir: Annotated[str, Field(description="本地文件目录", examples=[r"D:\code_project\ai_agent_with_langchain\.temp"])],
        vm_dest_dir: Annotated[str, Field(description="虚拟机文件目录", examples=[r"D:\code_project\ai_agent_with_langchain\.temp"])]
):
    if not os.path.exists(local_dir):
        msg = f"本地目录不存在：{local_dir}"
        print(f"[UPLOAD {msg}]")
        return msg
    if not os.path.isdir(local_dir):
        msg = f"指定路径不是文件夹：{local_dir}"
        print(f"[UPLOAD {msg}]")
        return msg

    make_dir_in_vm(vm_dest_dir)

    for root, dirs, files in os.walk(local_dir):
        if "node_modules" in dirs:
            dirs.remove("node_modules")
        if ".git" in dirs:
            dirs.remove(".git")

        rel_path = os.path.relpath(root, local_dir)
        vm_subdir = os.path.join(vm_dest_dir, rel_path)
        make_dir_in_vm(vm_subdir)

        for file_name in files:
            local_file_path = os.path.join(root, file_name)
            vm_file_path = os.path.join(vm_subdir, file_name)
            run_limavm_command(f"cp {local_file_path} lima-test:【{vm_file_path}】")

    return f"上传 【{local_dir}】目录至 lima-test:{vm_dest_dir} 成功"
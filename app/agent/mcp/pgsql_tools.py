# -*- coding: utf-8 -*-
"""
@Time : 2026/9/27 17:48
@Author: janic
@File: pgsql_tools.py
"""
from typing import Optional, Dict, Any, Annotated, List

import pymysql
import os
import psycopg
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP()


MYSQL_CONFIG = {
    "host": "127.0.0.1",  # 强制 IPv4，避免报错里的 ::1 超时
    "port": 5432,
    "dbname": "llmops",
    "user": "postgres",
    "password": "root"
}


class Response(BaseModel):
    success: bool
    database: str
    table: str
    data: Optional[dict] | Optional[list]
    rowcount: Optional[int] = None


def get_connection(dbname="llmops"):
    config = MYSQL_CONFIG.copy()
    if dbname:
        config["dbname"] = dbname
    try:
        connection = psycopg.connect(**config)
        return connection
    except Exception as e:
        msg = f"pgsql connection error: {str(e)}"
        # raise Exception(msg)
        return msg


def execute_query(command, database=None, params=None, commit=False):
    connection = get_connection(database)
    try:
        with connection.cursor() as cursor:
            cursor.execute(command, params)
            # 只有 SELECT 之类的查询才有 description，写操作没有结果集
            if cursor.description:
                result = cursor.fetchall()
            else:
                result = None
            # 写操作提交事务
            if commit:
                connection.commit()
            return result, cursor.rowcount
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()

@mcp.tool(name="pgsql_list_databases", description="列出包含的所有数据库")
def pgsql_list_databases():
    try:
        result, rowcount = execute_query("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = [row[0] for row in result]
        return Response(
            success=True,
            database="",
            table="",
            data=databases,
            rowcount=rowcount
        )
    except Exception as e:
        msg = f"list databases error: {str(e)}"
        return msg


@mcp.tool(name="pgsql_list_tables", description="列出指定数据库中包含的所有数据表")
def pgsql_list_tables(database):
    try:
        sql = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                  AND table_type = 'BASE TABLE';
                """
        result, rowcount = execute_query(sql, database=database)
        # 提取表名变成列表返回
        table_list = [row[0] for row in result]
        # print(f"数据库 '{database}' 中的表: {table_list}")
        return Response(
            success=True,
            database=database,
            table="",
            data=table_list,
            rowcount=rowcount
        )
    except Exception as e:
        msg = f"list tables error: {str(e)}"
        return msg


@mcp.tool(name="pgsql_describe_tables", description="获取表结构信息")
def pgsql_describe_tables(database: str, table: str):
    try:
        safe_table = table.replace("'", "''")  # 防止单引号导致的 SQL 注入

        sql = f"""
                SELECT 
                    column_name AS "字段名", 
                    data_type AS "数据类型", 
                    is_nullable AS "允许为空", 
                    column_default AS "默认值"
                FROM information_schema.columns
                WHERE table_schema = 'public' 
                  AND table_name = '{safe_table}';
                """
        result, rowcount = execute_query(sql, database=database)
        return Response(
            success=True,
            database=database,
            table=table,
            data=result,
            rowcount=rowcount
        )
    except Exception as e:
        msg = f"list tables error: {str(e)}"
        return msg


@mcp.tool(name="pgsql_execute_query", description="执行sql查询语句")
def pgsql_execute_query(command, database=None, params: Optional[list] = None):
    try:
        params_tuple = tuple(params) if params else None
        result, rowcount = execute_query(command, database=database, params=params_tuple)
        return Response(
            success=True,
            database=database,
            table="",
            data=result,
            rowcount=rowcount
        )
    except Exception as e:
        msg = f"execute query error: {str(e)}"
        return msg


@mcp.tool(name="pgsql_insert_data", description="向指定表中插入数据")
def pgsql_insert_data(database: str, table: str, data: Dict[str, str]):
    columns = list(data.keys())
    values = list(data.values())

    # 1. 对表名和字段名加双引号，防止保留字报错（如 user）
    safe_table = f'"{table}"'
    safe_columns = ', '.join([f'"{col}"' for col in columns])

    # 2. 使用 %s 占位符，而不是直接拼接值
    placeholders = ', '.join(['%s'] * len(values))

    command = f"INSERT INTO {safe_table} ({safe_columns}) VALUES ({placeholders})"

    try:
        # 传入 params 参数，并开启 commit
        result, rowcount = execute_query(command, database=database, params=values, commit=True)
        return Response(
            success=True,
            database=database,
            table=table,
            data=result,
            rowcount=rowcount
        )
    except Exception as e:
        msg = f"insert data error: {str(e)}"
        return msg

@mcp.tool(name="pgsql_update_data", description="更新指定数据表中的指定数据")
def pgsql_update_data(database: str, table: str, data: Dict[str, str], where: Dict[str, Any]):
    """
        更新数据。
        - data:  要更新的字段，如 {"name": "tom"}
        - where: WHERE 条件，如 {"id": 2}（推荐用字典，避免 SQL 注入）
        """
    safe_table = f'"{table}"'
    set_clause = ", ".join([f'"{k}" = %s' for k in data.keys()])
    where_clause = " AND ".join([f'"{k}" = %s' for k in where.keys()])

    command = f"UPDATE {safe_table} SET {set_clause} WHERE {where_clause}"
    # 参数顺序：先 SET 的值，后 WHERE 的值
    params = tuple(list(data.values()) + list(where.values()))

    try:
        result, rowcount = execute_query(command, database=database, params=params, commit=True)
        return Response(
            success=True,
            database=database,
            table=table,
            data=result,
            rowcount=rowcount
        )
    except Exception as e:
        # raise e
        msg = f"update data error: {str(e)}"
        return msg


@mcp.tool(name="pgsql_delete_data", description="删除指定数据表中的指定数据")
def pgsql_delete_data(database: str, table: str, where: Dict[str, Any]):
    """
        更新数据。
        - where: WHERE 条件，如 {"id": 2}（推荐用字典，避免 SQL 注入）
        """
    safe_table = f'"{table}"'
    # set_clause = ", ".join([f'"{k}" = %s' for k in data.keys()])
    where_clause = " AND ".join([f'"{k}" = %s' for k in where.keys()])

    command = f"DELETE FROM {safe_table} WHERE {where_clause}"
    # 参数顺序：先 SET 的值，后 WHERE 的值
    params = tuple(list(where.values()))

    try:
        result, rowcount = execute_query(command, database=database, params=params, commit=True)
        return Response(
            success=True,
            database=database,
            table=table,
            data=result,
            rowcount=rowcount
        )
    except Exception as e:
        # raise e
        msg = f"delete data error: {str(e)}"
        return msg


@mcp.tool(name="pgsql_create_database", description="创建新的数据库")
def pgsql_create_database(database_name: str, encoding: str = "UTF8"):
    """
        创建 PostgreSQL 数据库。
        - 必须连接到已有数据库（这里用 postgres）来执行 CREATE DATABASE
        - 必须使用 autocommit=True，因为 CREATE DATABASE 不能在事务中执行
        - encoding 默认 UTF8
        """
    # 连接到默认库 postgres
    config = MYSQL_CONFIG.copy()
    config["dbname"] = "postgres"

    try:
        # autocommit=True 是关键，否则会报 "cannot run inside a transaction block"
        with psycopg.connect(**config, autocommit=True) as conn:
            with conn.cursor() as cur:
                # 数据库名加双引号，防止关键字冲突；编码用 ENCODING
                # 用 sql.Identifier 更安全，避免 SQL 注入
                from psycopg import sql
                command = sql.SQL("CREATE DATABASE {} ENCODING {}").format(
                    sql.Identifier(database_name),
                    sql.Literal(encoding)
                )
                cur.execute(command)
        return Response(
            success=True,
            database=database_name,
            table="",
            data=None,
        )
    except Exception as e:
        raise e
        # msg = f"create database error: {str(e)}"
        # return msg


@mcp.tool(name="pgsql_create_table", description="创建新的数据表")
def pgsql_create_table(database: str,
                       table_name: str,
                       table_columns: Annotated[str, Field(description="建表语句中的字段部分")],
                       table_schema: Annotated[str, Field(description="建表语句中的补充部分")]):
    command = f"CREATE TABLE {table_name} ({table_columns}) {table_schema}"
    result, rowcount = execute_query(command, database)
    return Response(
        success=True,
        database=database,
        table=table_name,
        data=result,
        rowcount=rowcount
    )


@mcp.tool(name="pgsql_execute_command", description="执行特定的SQL语句")
def pgsql_execute_command(database: str, command: str):
    try:
        result, rowcount = execute_query(command, database)
        return Response(
            success=True,
            database=database,
            table="",
            data=result,
            rowcount=rowcount
        )
    except Exception as e:
        raise e


if __name__ == '__main__':
    # test_connection = get_connection()
    # print(test_connection)
    # print(mysql_describe_tables(database="llmops", table="user"))
    # print(pgsql_execute_query('select * from "user";', database="llmops"))
    # result = pgsql_insert_data("llmops", "user", {"id": "5", "name": "leo"})
    # print(result)
    # res = pgsql_update_data("llmops", "user", {"name": "tom"}, {"id": 2})
    # print(res)
    # res = pgsql_delete_data("llmops", "user", {"id": 3})
    # print(res)
    # res = pgsql_create_database("test")
    # print(res)
    res = pgsql_create_table("test")
    print(res)
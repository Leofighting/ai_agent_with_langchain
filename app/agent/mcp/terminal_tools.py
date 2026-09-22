# -*- coding: utf-8 -*-
"""
@Time : 2026/9/21 15:03
@Author: janic
@File: terminal_tools.py
"""
import subprocess
import time
from typing import Annotated
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP()


def run_applescript(script):
    p = subprocess.Popen(['osascript', "-e", script],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    output, error = p.communicate()
    return output.decode("utf-8").strip(), error.decode("utf-8").strip()


# @mcp.tool(name="get_all_terminal_ids", description="get all Terminal window and tab ids")
def get_all_terminal_ids() -> str:
    output, error = run_applescript("""
    tell application "Terminal"
        set outputList to {}
        repeat with aWindow in windows
            set windowID to id of aWindow
            set tabCount to number or tabs of aWindow
            repeat with tabIndex from 1 to tabCount
                set end of outputList to {tab tabIndex of window id windowID}
            end repeat
        end repeat
    end tell
    """)
    if error:
        return error
    return output


@mcp.tool(name="close_terminal_if_open", description="close Terminal application if it is open")
def close_terminal_if_open() -> str:
    output, error = run_applescript("""
    tell application "System Events"
        if exists "Terminal" then
            tell application "Terminal" to quit
        end if
    end tell
    """)
    if error:
        return f"failed: {error}"
    return "success"


@mcp.tool(name="open_new_terminal", description="open or activate a Terminal window")
def open_new_terminal(
        window_id: Annotated[str, Field(description="optional Terminal window id to activate; empty to open new",
                                        examples=["12345"])] = ""
) -> str:
    if window_id:
        output, error = run_applescript(f"""
        tell application "Terminal"
            if (count of windows) > 0 then
                set theWindow to window id {window_id}
                set frontmost of theWindow to true
                activate
            else
                activate
            end if
        end tell
        """)
    else:
        output, error = run_applescript(f"""
                tell application "Terminal"
                    activate
                end tell
                """)
    if error:
        return f"failed: {error}"
    time.sleep(5)
    return get_all_terminal_ids()


@mcp.tool(name="run_script_in_terminal", description="run a script in the front Terminal window")
def run_script_in_terminal(
        script: Annotated[str, Field(description="script command to run in Terminal",
                                     examples=["ls -al", "pwd"])]
) -> str:
    output, error = run_applescript(f"""
tell application "Terminal"
    activate
    if (count of windows) > 0 then
        do script "{script}" in window 1
    else
        do script "{script}"
    end if
end tell
""")
    if error:
        return error
    return output


@mcp.tool(name="get_terminal_full_text", description="get full history text of the selected Terminal tab")
def get_terminal_full_text() -> str:
    output, error = run_applescript(f"""
tell application "Terminal"
    set fullText to history of selected tab of front window
end tell
""")
    if error:
        return error
    return output


if __name__ == '__main__':
    # open_new_terminal()
    mcp.run(transport="stdio")

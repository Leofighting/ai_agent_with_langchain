# -*- coding: utf-8 -*-
"""
@Time : 2026/9/21 15:03
@Author: janic
@File: terminal_tools.py
"""
import subprocess
import time
from typing import Annotated, List
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


def parse_key_code(button):
    button = button.lower()

    keycode_map = {
        'return': 'return',
        'space': 'space',
        'up': 126,
        'down': 125,
        'left': 123,
        'right': 124,
        'a': 0,
        'b': 11,
        'c': 8,
        'd': 2,
        'e': 14,
        'f': 3,
        'g': 5,
        'h': 4,
        'i': 34,
        'j': 38,
        'k': 40,
        'l': 37,
        'm': 46,
        'n': 45,
        'o': 31,
        'p': 35,
        'q': 12,
        'r': 15,
        's': 1,
        't': 17,
        'u': 32,
        'v': 9,
        'w': 13,
        'x': 7,
        'y': 16,
        'z': 6,
        '.': 47,
        'dot': 47,
        '0': 29,
        '1': 18,
        '2': 19,
        '3': 20,
        '4': 21,
        '5': 23,
        '6': 22,
        '7': 26,
        '8': 28,
        '9': 25,
        '-': 27,
    }

    return keycode_map[button]


def concat_key_codes(key_codes):
    script = ''
    for key in key_codes:
        key_code = parse_key_code(key)
        script += f'keystroke {key_code}\n'
        script += 'delay 0.5\n'
    return script.strip()


@mcp.tool(name="send_terminal_keyboard_key", description="send a terminal keyboard key to an existing terminal")
def send_terminal_keyboard_key(key_codes: Annotated[List[str], Field(description="向终端输入一组按键", examples="['up', 'down']")]) -> bool:
    print('\nsend_terminal_keyboard_key keycode:', key_codes)
    print('-' * 50)
    script = f'''
tell application "Terminal"
    activate
    tell application "System Events"
        {concat_key_codes(key_codes)}
    end tell
end tell'''
    print(script)
    terminal_content, error = run_applescript(script)
    if error:
        return False
    else:
        return True


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

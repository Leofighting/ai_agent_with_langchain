# -*- coding: utf-8 -*-
"""
@Time : 2026/9/24 7:31
@Author: janic
@File: browser_tools.py
"""
import re
import time

from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from mcp.server.fastmcp import FastMCP
import undetected_chromedriver as uc
from undetected_chromedriver.options import ChromeOptions

mcp = FastMCP()


# def get_chrome_instance():
#     chrome_options = ChromeOptions()
#     chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
#     driver = uc.Chrome(options=chrome_options)
#     print(f"成功连接到 chrome 浏览器，当前url：{driver.current_url}")
#     time.sleep(5)
#     return driver

def get_chrome_instance():
    chromedriver_path = r"C:\Users\Administrator\Downloads\chromedriver-win64\chromedriver.exe"
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(options=chrome_options, service=service)
    print(f"成功连接到 chrome 浏览器，当前url：{driver.current_url}")
    time.sleep(5)
    return driver


def open_chrome(url):
    driver = get_chrome_instance()
    driver.get(url)
    all_handles = driver.window_handles
    print(all_handles)
    driver.switch_to.window(all_handles[-1])


@mcp.tool(
    name="query_rag_from_bing",
    description="search query on https://www.bing.com/"
)
def search_in_bing(query: str)->str:
    driver = webdriver.Chrome()
    try:
        driver.get("https://www.bing.com/")
        text_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "sb_form_q"))
        )
        text_box.send_keys(query)
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "search_icon"))
        )
        submit_button.click()
        search_li = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='sa_sug_block']/ul/li"))
        )
        search_li.click()
        WebDriverWait(driver, 5).until(
            EC.title_contains(query)
        )
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        page_content = driver.find_element(By.TAG_NAME, "body")
        print(page_content.get_attribute("innerHTML"))
        time.sleep(5)
    except Exception as e:
        print(e)
    finally:
        driver.quit()


# @mcp.tool(
#     name="query_rag_from_baidu",
#     description="search query on https://www.baidu.com/"
# )
def search_in_baidu(query: str)->str:
    driver = uc.Chrome()
    try:
        driver.get("https://www.baidu.com/")
        text_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "chat-textarea"))
        )
        text_box.send_keys(query)
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "chat-submit-button"))
        )
        submit_button.click()
        # search_li = WebDriverWait(driver, 5).until(
        #     EC.element_to_be_clickable((By.XPATH, "//div[@id='sa_sug_block']/ul/li"))
        # )
        # search_li.click()
        WebDriverWait(driver, 5).until(
            EC.title_contains(query)
        )

        page_text_list = []
        for i in range(3):
            if i > 0:
                result = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@class,'next_d-g2R')]"))
                )
                result.click()
                time.sleep(1)



            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            page_content = driver.find_element(By.TAG_NAME, "body")

            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            page_text = page_content.text
            page_text_list.append(page_text + "\n  -----  \n")
        # print(page_content.get_attribute("innerHTML"))
        time.sleep(35)
        return "\n".join(page_text_list)

    except Exception as e:
        print(e)
        return ""
    finally:
        driver.quit()


@mcp.tool(
    name="query_rag_from_baidu",
    description="search query on https://www.baidu.com/"
)
def search_in_baidu_with_html(query: str)->str:
    driver = uc.Chrome()
    try:
        driver.get("https://www.baidu.com/")
        text_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "chat-textarea"))
        )
        text_box.send_keys(query)
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "chat-submit-button"))
        )
        submit_button.click()
        # search_li = WebDriverWait(driver, 5).until(
        #     EC.element_to_be_clickable((By.XPATH, "//div[@id='sa_sug_block']/ul/li"))
        # )
        # search_li.click()
        WebDriverWait(driver, 5).until(
            EC.title_contains(query)
        )

        page_text_list = []
        for i in range(3):
            if i > 0:
                result = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@class,'next_d-g2R')]"))
                )
                result.click()
                time.sleep(1)



            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            page_content = driver.find_element(By.TAG_NAME, "body")

            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            page_text = page_content.text
            page_text_list.append(page_text)
        # print(page_content.get_attribute("innerHTML"))
        # time.sleep(35)
        html =  "\n".join(page_text_list)
        return pretty_html(html)

    except Exception as e:
        print(e)
        return ""
    finally:
        driver.quit()


def pretty_html(html: str)->str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "link", "meta", "symbol", "path", "canvas", "svg"]):
        tag.extract()

    display_none_re = re.compile(r"display\s*:\s*none", re.IGNORECASE)
    for tag in soup.find_all(True):
        style = tag.get("style", "")
        if display_none_re.search(style):
            tag.extract()

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    for tag in soup.find_all(True):
        if tag.name == "a":
            if "href" in tag.attrs:
                if "javascript" in tag.attrs["href"] or "/" == tag.attrs["href"]:
                    tag.extract()
                else:
                    tag.attrs = {"href": tag.attrs["href"]}
            else:
                tag.attrs = {}

    html = soup.prettify()
    return html


if __name__ == '__main__':
    # search_in_baidu("顺德的天气")
    # time.sleep(3)
    mcp.run(transport="stdio")
    # open_chrome()
    ...
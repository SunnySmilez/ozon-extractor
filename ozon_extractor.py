import sys
import os
import time

# 强制 PyInstaller 打包时包含所有 selenium 子模块
import selenium
import selenium.webdriver
import selenium.webdriver.chrome
import selenium.webdriver.chrome.webdriver
import selenium.webdriver.chrome.options
import selenium.webdriver.chrome.service
import selenium.webdriver.common.by
import selenium.webdriver.support.ui
import selenium.webdriver.support.expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC2
from selenium.webdriver.chrome.service import Service


def get_redirect_url(driver, url, timeout=15):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, timeout)
        try:
            elements = wait.until(
                EC2.presence_of_all_elements_located((By.CSS_SELECTOR, ".pdp_a8m a"))
            )
            links = []
            for el in elements:
                href = el.get_attribute("href")
                if href:
                    links.append(href)
            return links if links else ["[未找到链接]"]
        except Exception:
            elements = driver.find_elements(By.CSS_SELECTOR, ".pdp_a8m a")
            links = [el.get_attribute("href") for el in elements if el.get_attribute("href")]
            return links if links else ["[未找到 pdp_a8m 元素或链接]"]
    except Exception as e:
        return [f"[错误: {str(e)}]"]


def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("请输入包含URL的txt文件路径（可直接拖入文件）: ").strip().strip('"')

    if not os.path.exists(input_file):
        print(f"文件不存在: {input_file}")
        input("按回车退出...")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("文件中没有有效的URL！")
        input("按回车退出...")
        return

    print(f"共读取 {len(urls)} 个URL，开始处理...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    results = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] 处理: {url}")
        links = get_redirect_url(driver, url)
        for link in links:
            results.append(f"{url}\t{link}")
        time.sleep(2)

    driver.quit()

    input_dir = os.path.dirname(os.path.abspath(input_file))
    output_file = os.path.join(input_dir, "output_links.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("原始URL\t跳转链接\n")
        f.write("\n".join(results))

    print(f"\n完成！共处理 {len(urls)} 个URL")
    print(f"结果已保存到: {output_file}")
    input("按回车退出...")


if __name__ == "__main__":
    main()

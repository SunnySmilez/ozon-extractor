import sys
import os
import time
import random
import requests
from bs4 import BeautifulSoup

HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
]

def get_links(url, session, retries=3):
    for attempt in range(retries):
        try:
            headers = random.choice(HEADERS_LIST)
            resp = session.get(url, headers=headers, timeout=20, allow_redirects=True)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                # 找 class 包含 pdp_a8m 的元素里的 a 标签
                containers = soup.find_all(class_=lambda c: c and "pdp_a8m" in c.split())
                links = []
                for container in containers:
                    for a in container.find_all("a", href=True):
                        href = a["href"]
                        if href.startswith("/"):
                            href = "https://www.ozon.ru" + href
                        links.append(href)
                if links:
                    return links
                # 也直接搜索所有 a[href] 在 pdp_a8m class 里
                return ["[未找到 pdp_a8m 链接，页面可能需要登录或有反爬]"]
            elif resp.status_code == 429:
                wait = 10 * (attempt + 1)
                print(f"  被限速，等待 {wait}s...")
                time.sleep(wait)
            else:
                return [f"[HTTP {resp.status_code}]"]
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(5)
            else:
                return [f"[错误: {str(e)}]"]
    return ["[重试失败]"]

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

    session = requests.Session()
    # 先访问首页，获取 cookies
    try:
        session.get("https://www.ozon.ru", timeout=15)
    except:
        pass

    results = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] 处理: {url}")
        links = get_links(url, session)
        for link in links:
            print(f"  -> {link}")
            results.append(f"{url}\t{link}")
        time.sleep(random.uniform(2, 4))

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

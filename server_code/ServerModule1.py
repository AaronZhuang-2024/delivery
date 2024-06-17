import requests
from bs4 import BeautifulSoup
import random
import time
import anvil.server
from anvil import tables
from anvil.tables import app_tables

@anvil.server.callable
def search_and_store_delivery_notices(keyword, start_page, end_page):
    base_url = "https://www.gzcourt.gov.cn/other/ck601/index{}.html"
    user_agents = [
       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
       # 其他User-Agent
    ]
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept-Language': 'en-US,en;q=0.9'
    }

    def extract_delivery_notices(url, headers):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            print(f"Successfully fetched URL: {url}")  # Debug info
        except requests.RequestException as e:
            print(f"请求错误: {e}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        delivery_notices = soup.find_all('li')
        print(f"Found {len(delivery_notices)} notices on page")  # Debug info
        notices = []
        for notice in delivery_notices:
            a_tag = notice.find('a')
            if a_tag and 'href' in a_tag.attrs:
                title = a_tag.text.strip()
                link = "https://www.gzcourt.gov.cn" + a_tag['href']
                notices.append((title, link))
                print(f"Notice found: {title} - {link}")  # Debug info
            else:
                print("链接标签解析错误或缺少 href 属性。")
        return notices

    results = []
    for i in range(start_page, end_page + 1):
        if i == 1:
            url = "https://www.gzcourt.gov.cn/other/ck601/index.html"
        else:
            url = base_url.format(i - 1)
        
        notices = extract_delivery_notices(url, headers)
        for notice_title, notice_link in notices:
            # 转换为UTF-8编码进行匹配
            if keyword.encode('utf-8') in notice_title.encode('utf-8'):
                results.append(f"在第 {i} 页找到了对应公告：\n公告标题: {notice_title}\n公告链接: {notice_link}\n--------------------------------------\n")
        time.sleep(random.uniform(0.2, 0.5))
    
    print(f"Total notices found: {len(results)}")  # Debug info

    # 将结果存储到表格中
    app_tables.case_results.add_row(
        case_number=keyword,
        results='\n'.join(results) if results else "没有找到与任何案号相关的送达公告。"
    )
    
    return results


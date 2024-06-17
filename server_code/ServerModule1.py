import requests
from bs4 import BeautifulSoup
import random
import asyncio
from anvil.server import call
from anvil.tables import app_tables

@anvil.server.callable
async def search_and_store_delivery_notices(keyword, start_page, end_page, batch_size=10):
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

    async def process_batch(start, end):
        results = []
        for i in range(start, end + 1):
            if i == 1:
                url = "https://www.gzcourt.gov.cn/other/ck601/index.html"
            else:
                url = base_url.format(i - 1)
            
            notices = extract_delivery_notices(url, headers)
            for notice_title, notice_link in notices:
                # 转换为UTF-8编码进行匹配
                if keyword.encode('utf-8') in notice_title.encode('utf-8'):
                    results.append(f"在第 {i} 页找到了对应公告：\n公告标题: {notice_title}\n公告链接: {notice_link}\n--------------------------------------\n")
            await asyncio.sleep(random.uniform(0.2, 0.5))
        
        print(f"Processed batch from page {start} to {end}")  # Debug info
        return results

    # 计算总批次数
    total_batches = (end_page - start_page + 1) // batch_size + 1
    tasks = []

    # 异步处理每个批次
    for batch_start in range(start_page, end_page + 1, batch_size):
        batch_end = min(batch_start + batch_size - 1, end_page)
        tasks.append(process_batch(batch_start, batch_end))

    # 执行异步任务
    results = await asyncio.gather(*tasks)
    flattened_results = [item for sublist in results for item in sublist]

    print(f"Total notices found: {len(flattened_results)}")  # Debug info

    # 将结果存储到表格中
    app_tables.case_results.add_row(
        case_number=keyword,
        results='\n'.join(flattened_results) if flattened_results else "没有找到与任何案号相关的送达公告。"
    )
    
    return flattened_results

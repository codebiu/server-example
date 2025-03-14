import requests
from bs4 import BeautifulSoup
import os
from playsound import playsound

def download_mp3(url, save_path):
    """
    下载 MP3 文件并保存到指定路径。
    """
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"文件已保存到: {save_path}")
    else:
        print(f"下载失败，状态码: {response.status_code}")

def play_mp3(file_path):
    """
    播放 MP3 文件。
    """
    try:
        playsound(file_path)
    except Exception as e:
        print(f"播放失败: {e}")

def search_mp3_duckduckgo(query, save_dir="downloads"):
    """
    使用 DuckDuckGo 搜索并下载 MP3 文件。
    """
    # 创建保存目录
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # DuckDuckGo 搜索 URL
    search_url = f"https://duckduckgo.com/html/?q={query}+mp3"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # 发送搜索请求
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找 MP3 文件链接（根据 DuckDuckGo 搜索结果页面结构调整）
    mp3_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.mp3'):
            mp3_links.append(href)

    if not mp3_links:
        print("未找到 MP3 文件")
        return

    # 下载第一个 MP3 文件
    mp3_url = mp3_links[0]
    save_path = os.path.join(save_dir, f"{query}.mp3")
    download_mp3(mp3_url, save_path)

    # 播放 MP3 文件
    play_mp3(save_path)

if __name__ == "__main__":
    # 搜索并下载周杰伦的 MP3 文件
    search_mp3_duckduckgo("周杰伦")
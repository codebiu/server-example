import asyncio
import ssl
from urllib.parse import urlparse
import socket
async def fetch_url(url, port=None, use_ssl=None):
    # 解析URL
    parsed = urlparse(url)
    host = parsed.netloc
    path = parsed.path if parsed.path else "/"
    
    # 自动确定端口和SSL
    if port is None:
        port = 443 if parsed.scheme == 'https' else 80
    if use_ssl is None:
        use_ssl = parsed.scheme == 'https'

    # 创建SSL上下文（如果需要）
    ssl_context = ssl.create_default_context() if use_ssl else None
    
    # 建立连接
    reader, writer = await asyncio.open_connection(
        host=host,
        port=port,
        ssl=ssl_context,
        proto=socket.IPPROTO_TCP
    )

    try:
        # 发送HTTP请求
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "User-Agent: Python-asyncio\r\n"
            "Connection: close\r\n\r\n"
        )
        writer.write(request.encode())
        await writer.drain()

        # 读取响应头
        headers = await reader.readuntil(b"\r\n\r\n")
        
        # 检查是否为分块传输编码
        if b"Transfer-Encoding: chunked" in headers:
            body = await read_chunked(reader)
        else:
            body = await reader.read()

        return body.decode('utf-8', errors='ignore')

    finally:
        writer.close()
        await writer.wait_closed()

async def read_chunked(reader):
    """处理分块传输编码"""
    data = []
    while True:
        chunk_size_line = await reader.readuntil(b"\r\n")
        chunk_size = int(chunk_size_line.strip(), 16)
        if chunk_size == 0:
            break
        data.append(await reader.readexactly(chunk_size))
        await reader.read(2)  # 跳过\r\n
    return b"".join(data)

async def main():
    # curl https://www.google.com.hk
    # 测试不同场景
    test_urls = [
        ("https://www.baidu.com", None, None),  # 自动判断(https)
        ("https://www.google.com", None, None),  # 自动判断(https)
        ("http://example.com", 80, False),    # 明确指定不使用SSL
        ("https://github.com", 443, True),    # 明确指定使用SSL
        ("http://example.org", None, None)    # 自动判断(http)
    ]
    
    for url, port, use_ssl in test_urls:
        print(f"\nFetching {url} (port={port}, ssl={use_ssl})")
        try:
            html = await fetch_url(url, port, use_ssl)
            if html:
                title = html.split("<title>")[1].split("</title>")[0][:50] if "<title>" in html else "No title"
                print(f"Success! Title: {title}...")
            else:
                print("Got empty response")
        except Exception as e:
            print(f"Error: {str(e)}")

asyncio.run(main())

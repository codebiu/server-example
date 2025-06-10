import asyncio
import ssl
from urllib.parse import urlparse

async def fetch_https(url):
    parsed = urlparse(url)
    host = parsed.netloc
    path = parsed.path if parsed.path else "/"
    port = 443  # 强制HTTPS端口

    # 创建SSL安全上下文
    ssl_context = ssl.create_default_context()
    
    # 建立异步SSL连接
    reader, writer = await asyncio.open_connection(
        host=host,
        port=port,
        ssl=ssl_context
    )

    try:
        # 发送HTTP请求（必须包含Host头）
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
            break  # 结束标志
        data.append(await reader.readexactly(chunk_size))
        await reader.read(2)  # 跳过\r\n
    return b"".join(data)

async def main():
    html = await fetch_https("https://github.com")
    if html:
        print(html.split("<title>")[1].split("</title>")[0])

asyncio.run(main())
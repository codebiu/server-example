import os
import json
import asyncio
import subprocess
from asyncio.subprocess import Process

# 缓存区，用于存储从语言服务器接收到的数据。
buffer = bytearray()

# 用来保存解析出的消息头中的内容长度。
header_content_length = None

# 记录所有已发出但尚未收到响应的请求及其对应的计时器。
outstanding_requests_with_id = {}

# 用于等待接收到来自语言服务器的消息。
received_event = asyncio.Event()
received_message = None

# 初始化通知的消息体。
init_notification = {
    'jsonrpc': '2.0',
    'method': 'initialized',
    'params': {}
}

# 跟踪迄今为止看到的最大 ID 以避免重复。
largest_id_seen = 3

verbosity = 0

def goto_def(request_id, uri, line, char):
    return {
        'jsonrpc': '2.0',
        'id': request_id,
        'method': 'textDocument/definition',
        'params': {
            'textDocument': {'uri': str(uri)},
            'position': {'line': line, 'character': char}
        }
    }

def init_message(process_id, root_uri):
    root_path = root_uri
    name = os.path.basename(root_uri)
    if not name:
        name = os.path.basename(os.path.dirname(root_uri))
    return {
        'id': 0,
        'jsonrpc': '2.0',
        'method': 'initialize',
        'params': {
            'processId': process_id,
            'clientInfo': {'name': 'lspTestScript', 'version': '0.0.1'},
            'locale': 'en',
            'rootPath': root_path,
            'rootUri': str(root_uri),
            'capabilities': {},
            'initializationOptions': {},
            'workspaceFolders': [
                {'uri': str(root_uri), 'name': name}
            ]
        }
    }

def init_more(sdk_uri):
    return {
        'id': 1,
        'jsonrpc': '2.0',
        'result': [
            {
                'useLsp': True,
                'sdkPath': str(sdk_uri),
                'allowAnalytics': False,
            }
        ]
    }

def ends_with_crlfcrlf(buffer):
    return len(buffer) > 4 and buffer[-4:] == b'\r\n\r\n'

async def listen_to_stdout(process):
    global buffer, header_content_length, received_event, received_message
    while True:
        data = await process.stdout.read(1)
        if not data:
            break

        buffer.extend(data)

        if ends_with_crlfcrlf(buffer):
            header_raw = buffer.decode()
            buffer.clear()
            headers = header_raw.split('\r\n')
            for header in headers:
                if header.startswith('Content-Length:'):
                    header_content_length = int(header.split(':')[1].strip())
                    break
        elif header_content_length is not None and len(buffer) == header_content_length:
            message_string = buffer.decode()
            buffer.clear()
            header_content_length = None

            message = json.loads(message_string)
            possible_id = message.get('id')

            if possible_id and isinstance(possible_id, int):
                global largest_id_seen
                largest_id_seen = max(largest_id_seen, possible_id)

                stopwatch = outstanding_requests_with_id.pop(possible_id, None)
                if stopwatch and verbosity > 2:
                    print(f"Received response for ID {possible_id} in {stopwatch.elapsed()} seconds")

            received_message = message
            received_event.set()

async def send(process, json_data):
    global largest_id_seen
    json_encoded_body = json.dumps(json_data).encode('utf-8')
    header = f"Content-Length: {len(json_encoded_body)}\r\nContent-Type: application/vscode-jsonrpc; charset=utf-8\r\n\r\n".encode('ascii')

    possible_id = json_data.get('id')
    if possible_id and isinstance(possible_id, int):
        largest_id_seen = max(largest_id_seen, possible_id)
        outstanding_requests_with_id[possible_id] = asyncio.get_event_loop().time()

    process.stdin.write(header)
    process.stdin.write(json_encoded_body)
    await process.stdin.drain()

async def main():
    root_uri = 'D:/project/test/sdk-3.5.0/pkg/analysis_server/tool/spec'
    sdk_uri = 'D:/a_code_lib/jdks/android/flutter_windows_3.24.5-stable/flutter/bin/cache/dart-sdk'
    click_on_uri = 'D:/project/test/sdk-3.5.0/pkg/analysis_server/tool/spec/check_all_test.dart'
    click_line, click_column = 18, 31
    every_ms = 100

    if not os.path.exists(sdk_uri):
        raise FileNotFoundError(f"Directory {sdk_uri} does not exist.")

    if not os.path.isfile(click_on_uri):
        raise FileNotFoundError(f"File {click_on_uri} does not exist.")

    process = await asyncio.create_subprocess_exec(
        'dart', 'language-server', '--diagnostic-port=8100',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE
    )

    asyncio.create_task(listen_to_stdout(process))

    await send(process, init_message(os.getpid(), root_uri))
    await received_event.wait()
    received_event.clear()

    await send(process, init_notification)
    await received_event.wait()
    received_event.clear()

    await send(process, init_more(sdk_uri))
    await received_event.wait()
    received_event.clear()

    await send(process, goto_def(largest_id_seen + 1, click_on_uri, click_line, click_column))
    await asyncio.sleep(every_ms / 1000)

    print('Delay completed after', every_ms / 1000, 'seconds.')

asyncio.run(main())

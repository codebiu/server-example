from typing import *
import time
import logging
import numpy as np
import asyncio
import time
import io
import re
import requests

logger = logging.getLogger(__file__)

splitter = re.compile(r'[,，。.!?！？;；、\n]')


class TTSResult:
    def __init__(self, pcm_bytes: bytes, finished: bool):
        self.pcm_bytes = pcm_bytes
        self.finished = finished
        self.progress: float = 0.0
        self.elapsed: float = 0.0
        self.audio_duration: float = 0.0
        self.audio_size: int = 0

    def to_dict(self):
        return {
            "progress": self.progress,
            "elapsed": f'{int(self.elapsed * 1000)}ms',
            "duration": f'{self.audio_duration:.2f}s',
            "size": self.audio_size
        }


class TTSStream:
    def __init__(self, engine, sid: int, speed: float = 1.0, sample_rate: int = 16000, original_sample_rate: int = 16000):
        self.engine = engine
        self.sid = sid
        self.speed = speed
        self.outbuf: asyncio.Queue[TTSResult | None] = asyncio.Queue()
        self.is_closed = False
        self.target_sample_rate = sample_rate
        self.original_sample_rate = original_sample_rate

    def on_process(self, text: str):
        url = "https://api.siliconflow.cn/v1/audio/speech"

        payload = {
            "model": "FunAudioLLM/CosyVoice2-0.5B",
            "input": text,
            "voice": "FunAudioLLM/CosyVoice2-0.5B:claire",
            "response_format": "pcm",
            "sample_rate": 16000,
            "stream": False,
            "speed": 1,
            "gain": 0
        }
        key = ''
        headers = {
            "Authorization": "Bearer "+key,
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        # 获取响应的二进制内容（PCM 数据）
        return response.content


    async def write(self, text: str, split: bool, pause: float = 0.2):
        start = time.time()
        #if split:
        texts = re.split(splitter, text)
        #else:
        #    texts = [text]

        audio_duration = 0.0
        audio_size = 0

        for idx, text in enumerate(texts):
            text = text.strip()
            if not text:
                continue
            sub_start = time.time()

            
            pcm_bytes = await asyncio.to_thread(self.on_process, text)
            
            self.outbuf.put_nowait(TTSResult(pcm_bytes, False))


        r = TTSResult(None, True)
        r.progress = 1.0
        r.finished = True
        await self.outbuf.put(r)

    async def close(self):  
        self.is_closed = True
        self.outbuf.put_nowait(None)
        logger.info("tts: stream closed")

    async def read(self) -> TTSResult:
        return await self.outbuf.get()

    async def generate(self,  text: str) -> io.BytesIO:
        output = io.BytesIO()
        return output


async def start_tts_stream(sid: int, sample_rate: int, speed: float, args) -> TTSStream:
    return TTSStream(sid, sample_rate, speed, args)

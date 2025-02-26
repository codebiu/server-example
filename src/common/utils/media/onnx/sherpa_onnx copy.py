import asyncio
import numpy as np
import sounddevice as sd
from pathlib import Path
import sherpa_onnx

class RealTimeSpeechRecognizer:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        self.recognizer = sherpa_onnx.OnlineRecognizer.from_pretrained(model=model_dir)
        self.sample_rate = 16000

    async def recognize_from_microphone(self):
        # 配置音频流参数
        channels = 1
        dtype = 'int16'

        # 打开麦克风流
        stream = sd.InputStream(samplerate=self.sample_rate, channels=channels, dtype=dtype, callback=self.audio_callback)

        print("开始实时语音识别（按 Ctrl+C 停止）...")
        with stream:
            while True:
                await asyncio.sleep(0.1)  # 让出控制权

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        
        # 将音频数据转换为 float32 并添加到缓冲区
        audio_data = indata.copy().astype(np.float32).flatten() / 32768.0
        self.process_audio(audio_data)

    def process_audio(self, audio_data):
        samples_per_frame = 160  # 模型期望的帧长度
        frame_shift_ms = 10  # 帧移（毫秒）
        sample_rate = 16000

        for start in range(0, len(audio_data), int(sample_rate * frame_shift_ms / 1000)):
            end = start + samples_per_frame
            if end > len(audio_data):
                break

            frame = audio_data[start:end]
            self.recognizer.accept_waveform(sample_rate, frame)

            if self.recognizer.is_endpoint():
                result = self.recognizer.decode()
                print(f"识别结果: {result.text}")
                self.recognizer.reset()

if __name__ == "__main__":
    model_dir = "/path/to/sherpa-onnx-models/your-model-dir"  # 替换为你的模型路径
    recognizer = RealTimeSpeechRecognizer(model_dir)
    
    try:
        asyncio.run(recognizer.recognize_from_microphone())
    except KeyboardInterrupt:
        print("停止实时语音识别")




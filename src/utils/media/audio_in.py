import pyaudio
import wave

# 录音参数
FORMAT = pyaudio.paInt16  # 音频格式（16位PCM）
CHANNELS = 1              # 单声道
RATE = 44100              # 采样率
CHUNK = 1024              # 数据块大小
RECORD_SECONDS = 5        # 录音时间
WAVE_OUTPUT_FILENAME = "output.wav"  # 输出文件名

# 初始化PyAudio
audio = pyaudio.PyAudio()

# 打开麦克风流
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

print("开始录音...")

frames = []

# 录制音频数据
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("录音结束.")

# 停止和关闭流
stream.stop_stream()
stream.close()
audio.terminate()

# 将录音保存到文件
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(audio.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print(f"文件已保存为 {WAVE_OUTPUT_FILENAME}")
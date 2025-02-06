import sherpa_onnx

# 1. 配置模型路径
model_config = sherpa_onnx.OfflineRecognizerConfig(
    # 模型文件路径
    model="sherpa-onnx-conformer-en-2023-03-28/model.onnx",
    tokens="sherpa-onnx-conformer-en-2023-03-28/tokens.txt",
    # 解码方法（greedy_search 或 modified_beam_search）
    decoding_method="greedy_search",
    # 其他参数
    num_threads=4,  # 使用的线程数
    debug=False,    # 是否启用调试模式
)

# 2. 创建离线识别器
recognizer = sherpa_onnx.OfflineRecognizer(model_config)

# 3. 加载音频文件
audio = sherpa_onnx.read_wave("path/to/your/audio.wav")

# 4. 创建音频流
stream = recognizer.create_stream()
stream.accept_waveform(sample_rate=audio.sample_rate, waveform=audio.samples)

# 5. 解码音频
recognizer.decode_stream(stream)

# 6. 获取识别结果
result = stream.result
print("识别结果:", result.text)
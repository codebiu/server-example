import time
import ffmpeg, wave
import numpy as np
import sherpa_onnx


if __name__ == "__main__":
    # https://k2-fsa.github.io/sherpa/onnx/pretrained_models/index.html
    from config.path import dir_temp
    from pathlib import Path

    model_dir = (
        Path(dir_temp)
        / "model\\sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20"
    )

    # 使用FFmpeg将音频文件转换为适合识别的格式并读取音频数据
    def read_audio_with_ffmpeg(wave_filename):
        # 使用FFmpeg将音频文件转换为浮动精度（float32）格式
        out, _ = (
            ffmpeg.input(wave_filename)
            .output(
                "pipe:", format="s16le", ac=1
            )  # 's16le' 代表16-bit little-endian PCM，ac=1是单声道
            .run(capture_stdout=True, capture_stderr=True)
        )

        # 将字节流转换为int16并标准化到-1到1之间
        samples_int16 = np.frombuffer(out, dtype=np.int16)
        samples_float32 = samples_int16.astype(np.float32)
        samples_float32 = samples_float32 / 32768  # 归一化到[-1, 1]

        # 获取采样率
        probe = ffmpeg.probe(
            wave_filename,
            v="error",
            select_streams="a:0",
            show_entries="stream=sample_rate",
        )
        sample_rate = int(probe["streams"][0]["sample_rate"])
        # 样本值 采样率
        return samples_float32, sample_rate

    def read_audio_with_ffmpeg_optimized(wave_filename, target_sample_rate=16000):
        """优化后的音频读取函数

        参数:
            wave_filename (str): 音频文件路径
            target_sample_rate (int): 目标采样率（默认16000）

        返回:
            samples_float32 (np.ndarray): 归一化到 [-1, 1] 的浮点音频数据
            target_sample_rate (int): 固定目标采样率
        """
        # 单次 FFmpeg 调用完成所有处理
        out, _ = (
            ffmpeg.input(wave_filename)
            .output(
                "pipe:",
                format="f32le",  # 直接输出 float32 格式，避免后续转换
                ac=1,  # 单声道
                ar=target_sample_rate,  # 指定目标采样率，避免探测原始采样率
            )
            .run(capture_stdout=True, capture_stderr=True, quiet=True)
        )

        # 直接从字节流转换为 float32 数组（FFmpeg 已处理归一化）
        samples_float32 = np.frombuffer(out, dtype=np.float32)

        return samples_float32, target_sample_rate

    def read_wave(wave_filename: str):
        with wave.open(wave_filename) as f:
            assert f.getnchannels() == 1, f.getnchannels()
            assert f.getsampwidth() == 2, f.getsampwidth()  # it is in bytes
            num_samples = f.getnframes()
            samples = f.readframes(num_samples)
            samples_int16 = np.frombuffer(samples, dtype=np.int16)
            samples_float32 = samples_int16.astype(np.float32)

            samples_float32 = samples_float32 / 32768
            return samples_float32, f.getframerate()

    # # 加载Sherpa ONNX模型

    recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
        # recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=str(model_dir / "encoder-epoch-99-avg-1.onnx"),  # 你的encoder模型路径
        decoder=str(model_dir / "decoder-epoch-99-avg-1.onnx"),  # 你的解码器模型路径
        joiner=str(model_dir / "joiner-epoch-99-avg-1.onnx"),  # 你的joiner模型路径
        tokens=str(model_dir / "tokens.txt"),  # 你的token文件路径
        num_threads=4,
        sample_rate=16000,  # 目标采样率
        feature_dim=80,  # 特征维度
        decoding_method="greedy_search",  # 解码方式
    )

    # 加载音频文件
    audio_path = (
        "test-data/ai_model/output.wav"  # 这里你可以使用任何音频格式（例如MP3、WAV等）
    )

    start_time = time.time()
    # samples_float32, sample_rate = read_audio_with_ffmpeg(audio_path)
    # samples_float32, sample_rate = read_audio_with_ffmpeg_optimized(audio_path)

    samples_float32, sample_rate = read_wave(audio_path)
    print("test", time.time() - start_time)
    # 使用模型进行识别
    s = recognizer.create_stream()

    # 将音频样本数据分批传入并进行实时识别
    # s.accept_waveform(sample_rate,samples_float32)  # 传递音频数据
    # recognizer.decode_stream(s)
    s.accept_waveform(sample_rate, samples_float32)

    # tail_paddings = np.zeros(int(0.66 * sample_rate), dtype=np.float32)
    # s.accept_waveform(sample_rate, tail_paddings)
    while recognizer.is_ready(s):
        recognizer.decode_stream(s)
    # 获取识别结果
    result = recognizer.get_result(s)

    # 输出识别结果
    print("识别结果:", result)

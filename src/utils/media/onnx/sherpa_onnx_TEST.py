import ffmpeg,wave
import numpy as np
import sherpa_onnx


if __name__ == "__main__":
    from config.path import dir_temp

    model_dir = dir_temp + "\\model\\"

    # 使用FFmpeg将音频文件转换为适合识别的格式并读取音频数据
    def read_audio_with_ffmpeg(wave_filename):
        # 使用FFmpeg将音频文件转换为浮动精度（float32）格式
        out, _ = (
            ffmpeg.input(wave_filename)
            .output('pipe:', format='s16le', ac=1)  # 's16le' 代表16-bit little-endian PCM，ac=1是单声道
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        # 将字节流转换为int16并标准化到-1到1之间
        samples_int16 = np.frombuffer(out, dtype=np.int16)
        samples_float32 = samples_int16.astype(np.float32)
        samples_float32 = samples_float32 / 32768  # 归一化到[-1, 1]
        
        # 获取采样率
        probe = ffmpeg.probe(wave_filename, v='error', select_streams='a:0', show_entries='s=sample_rate')
        sample_rate = int(probe['streams'][0]['sample_rate'])
        # 样本值 采样率
        return samples_float32, sample_rate

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
    # 加载Sherpa ONNX模型
    
    recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
    # recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(

        encoder=model_dir + "encoder-epoch-99-avg-1.onnx",  # 你的encoder模型路径
        decoder=model_dir + "decoder-epoch-99-avg-1.onnx",  # 你的解码器模型路径
        joiner=model_dir + "joiner-epoch-99-avg-1.onnx",  # 你的joiner模型路径
        tokens=model_dir + "tokens.txt",  # 你的token文件路径
        num_threads=4,
        sample_rate=16000,  # 目标采样率
        feature_dim=80,  # 特征维度
        decoding_method="greedy_search",  # 解码方式
    )

    # 加载音频文件
    audio_path = (
        "test-data/ai_model/test.wav"  # 这里你可以使用任何音频格式（例如MP3、WAV等）
    )
    # samples_float32, sample_rate = read_audio_with_ffmpeg(audio_path)
    samples_float32, sample_rate = read_wave(audio_path)

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
    result =recognizer.get_result(s)

    # 输出识别结果
    print("识别结果:", result)
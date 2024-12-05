import numpy as np
import sherpa_onnx

from pydub import AudioSegment

def extract_audio_segment(audio_path, start_time, end_time):
    audio = AudioSegment.from_wav(audio_path)
    return audio[start_time * 1000:end_time * 1000]  # 转换为毫秒




if __name__ == "__main__":
    # 模型输出和加载
    path_model = "source/test/linear_regression_fixed.onnx"
    
    # 加载说话人识别模型
    speaker_model = sherpa_onnx.SpeakerModel(model_path="source/test/sherpa_onnx/speaker_model.onnx")
    # 加载语音识别模型
    asr_model = sherpa_onnx.ASRModel(model_path="source/test/sherpa_onnx/asr_model.onnx")

    # 加载音频文件
    audio_path = "path/to/audio/file.wav"

    # 使用 VAD 检测音频中的语音部分
    vad_segments = speaker_model.detect_speech(audio_path)

    for segment in vad_segments:
        start_time, end_time = segment
        print(f"Detected speech from {start_time}s to {end_time}s")
        
        # 提取音频片段
        audio_segment = extract_audio_segment(audio_path, start_time, end_time)
        
        # 进行说话人识别
        speaker_id = speaker_model.predict(audio_segment)
        print(f"Identified speaker: {speaker_id}")

        # 进行语音识别
        transcription = asr_model.transcribe(audio_segment)
        print(f"Transcription: {transcription}")

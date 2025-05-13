from typing import *
import logging
import time
import logging
import uuid
import wave
import sherpa_onnx
import os
import asyncio
import numpy as np

logger = logging.getLogger(__file__)
_asr_engines = {}


class ASRResult:
    def __init__(self, text: str, finished: bool, idx: int):
        self.text = text
        self.finished = finished
        self.idx = idx

    def to_dict(self):
        return {"text": self.text, "finished": self.finished, "idx": self.idx}


class ASRStream:
    def __init__(self, recognizer: Union[sherpa_onnx.OnlineRecognizer | sherpa_onnx.OfflineRecognizer], sample_rate: int) -> None:
        self.recognizer = recognizer
        self.inbuf = asyncio.Queue()
        self.outbuf = asyncio.Queue()
        self.sample_rate = sample_rate
        self.is_closed = False
        self.online = isinstance(recognizer, sherpa_onnx.OnlineRecognizer)
        self.uuid = str(uuid.uuid4())
        self.vad = load_vad_engine_self(sample_rate,"cpu")

    async def start(self):
        if self.online:
            asyncio.create_task(self.run_online())
        else:
            # asyncio.create_task(self.run_offline())
            asyncio.create_task(self.run_offline_full())

    async def run_online(self):
        stream = self.recognizer.create_stream()
        last_result = ""
        segment_id = 0
        logger.info('asr: start real-time recognizer')
        while not self.is_closed:
            samples = await self.inbuf.get()
            stream.accept_waveform(self.sample_rate, samples)
            while self.recognizer.is_ready(stream):
                self.recognizer.decode_stream(stream)

            is_endpoint = self.recognizer.is_endpoint(stream)
            result = self.recognizer.get_result(stream)

            if result and (last_result != result):
                last_result = result
                logger.info(f' > {segment_id}:{result}')
                self.outbuf.put_nowait(
                    ASRResult(result, False, segment_id))

            if is_endpoint:
                if result:
                    logger.info(f'{segment_id}: {result}')
                    self.outbuf.put_nowait(
                        ASRResult(result, True, segment_id))
                    segment_id += 1
                self.recognizer.reset(stream)

    async def run_offline(self):
        vad = self.vad
        segment_id = 0
        st = None
        speech_detected = False
        while not self.is_closed:
            samples = await self.inbuf.get()
            vad.accept_waveform(samples)
            # 检测语音活动
            if vad.is_speech_detected() and not speech_detected:
                self.outbuf.put_nowait(ASRResult("@start@", False, segment_id))
                segment_id += 1
                speech_detected = True
            elif not vad.is_speech_detected() and speech_detected:
                speech_detected = False
            while not vad.empty():
                if not st:
                    st = time.time()
                stream = self.recognizer.create_stream()
                samples_new = add_silence(vad.front.samples, self.sample_rate, 200)
                stream.accept_waveform(self.sample_rate, samples_new)
                # sherpa_onnx.write_wave(f'./tmp/{self.uuid}{segment_id}.wav', samples_new, self.sample_rate)
                vad.pop()
                self.recognizer.decode_stream(stream)
                result = stream.result.text.strip()
                if result:
                    # result+= self.uuid
                    duration = time.time() - st
                    logger.info(f'{segment_id} {self.uuid}:{result} ({duration:.2f}s)')
                    self.outbuf.put_nowait(ASRResult(result, True, segment_id))
                    segment_id += 1
            st = None
    async def run_offline_full(self):
        """预留收音,防止vad丢字节"""
        vad = self.vad
        segment_id = 0
        st = None
        speech_detected = False
        # 50ms前移收音
        maxsize_this = 50 #*8 ms
        vioce_before = asyncio.Queue(maxsize=maxsize_this)
        vioce_this = []
        while not self.is_closed:
            samples = await self.inbuf.get()
            vad.accept_waveform(samples)
            if vioce_before.full():
                vioce_before.get_nowait()
            # 检测语音活动
            if vad.is_speech_detected() and not speech_detected:
                logger.info(f'{segment_id} {self.uuid}:"@start@"')
                vioce_this = []
                self.outbuf.put_nowait(ASRResult("@start@", False, segment_id))
                segment_id += 1
                speech_detected = True
            elif not vad.is_speech_detected() and speech_detected:
                speech_detected = False
                # logger.info(f'{segment_id} {self.uuid}:"@end@"')
            if not speech_detected:
                vioce_before.put_nowait(samples)
                # logger.info(f'{segment_id} {self.uuid}:{vioce_before.qsize()} "@insert@"')
            else:
                vioce_this.append(samples)
            while not vad.empty():
                if not st:
                    st = time.time()
                stream = self.recognizer.create_stream()
                
                vioce_this = np.array(vioce_this).flatten()
                samples_new_before,pre_buffer_samples=add_silence_before(vioce_before,vioce_this)
                vioce_before = asyncio.Queue(maxsize=maxsize_this)
                samples_new = add_silence(samples_new_before, self.sample_rate, 200)
                stream.accept_waveform(self.sample_rate, samples_new)
                # sherpa_onnx.write_wave(f'./tmp/{self.uuid}{segment_id}_0.wav', pre_buffer_samples, self.sample_rate)
                # sherpa_onnx.write_wave(f'./tmp/{self.uuid}{segment_id}_1.wav', vioce_this, self.sample_rate)
                # sherpa_onnx.write_wave(f'./tmp/{self.uuid}{segment_id}.wav', samples_new_before, self.sample_rate)
                vad.pop()
                self.recognizer.decode_stream(stream)
                result = stream.result.text.strip()
                if result and result != '。':
                    # result+= self.uuid
                    duration = time.time() - st
                    logger.info(f'{segment_id} {self.uuid}:{result} ({duration:.2f}s)')
                    self.outbuf.put_nowait(ASRResult(result, True, segment_id))
                    segment_id += 1
            st = None

    async def close(self):
        self.is_closed = True
        self.outbuf.put_nowait(None)

    async def write(self, pcm_bytes: bytes):
        pcm_data = np.frombuffer(pcm_bytes, dtype=np.int16)
        samples = pcm_data.astype(np.float32) / 32768.0
        self.inbuf.put_nowait(samples)

    async def read(self) -> ASRResult:
        return await self.outbuf.get()
    
    
def add_silence(samples, sample_rate=16000, silence_duration_ms=200):
    """
    在音频样本两端添加指定时长的静音帧。
    
    :param samples: 输入的音频样本，可以是列表或numpy array 格式
    :param sample_rate: 音频的采样率
    :param silence_duration_ms: 要添加的静音帧时长（毫秒）
    :return: 添加静音帧后的音频样本，返回为numpy array
    """
    samples = np.array(samples)  # 将输入样本转换为numpy数组
    samples_per_200ms = int(sample_rate * silence_duration_ms / 1000)
    silence = np.zeros(samples_per_200ms, dtype=samples.dtype)
    return np.concatenate((silence, samples, silence))

def add_silence_before(pre_buffer,vioce_this):
    """
    在音频样本左端添加指定时长的切除音频。
    :pre_buffer: 输入的音频样本，可以是列表或numpy array 格式
    :vad_samples: 音频的采样率

    """
    # 从 pre_buffer 中获取所有帧并拼接
    # vad_samples = np.array(vad_samples)
    pre_buffer_samples = []
    if not pre_buffer.empty():
        pre_buffer_samples = list(pre_buffer._queue)
        # pre_buffer._queue.clear()
    pre_buffer_samples = np.concatenate(pre_buffer_samples)
        # 将 pre_buffer_samples 与 vad.front.samples 拼接
    combined_samples = np.concatenate((pre_buffer_samples, vioce_this))
    return combined_samples,pre_buffer_samples
# def add_silence_before(pre_buffer,vad_samples):
#     """
#     在音频样本左端添加指定时长的切除音频。
#     :pre_buffer: 输入的音频样本，可以是列表或numpy array 格式
#     :vad_samples: 音频的采样率

#     """
#     # 从 pre_buffer 中获取所有帧并拼接
#     # vad_samples = np.array(vad_samples)
#     pre_buffer_samples = []
#     if not pre_buffer.empty():
#         pre_buffer_samples = list(pre_buffer._queue)
#         # pre_buffer._queue.clear()
#     if pre_buffer_samples:
#         pre_buffer_samples = np.concatenate(pre_buffer_samples)
#         # 将 pre_buffer_samples 与 vad.front.samples 拼接
#         combined_samples = np.concatenate((pre_buffer_samples, vad_samples))
#     else:
#         combined_samples = vad_samples
#     return combined_samples,pre_buffer_samples


def create_zipformer(samplerate: int, args) -> sherpa_onnx.OnlineRecognizer:
    d = os.path.join(
        args.models_root, 'sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20')
    if not os.path.exists(d):
        raise ValueError(f"asr: model not found {d}")

    encoder = os.path.join(d, "encoder-epoch-99-avg-1.onnx")
    decoder = os.path.join(d, "decoder-epoch-99-avg-1.onnx")
    joiner = os.path.join(d, "joiner-epoch-99-avg-1.onnx")
    tokens = os.path.join(d, "tokens.txt")

    recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
        tokens=tokens,
        encoder=encoder,
        decoder=decoder,
        joiner=joiner,
        provider=args.asr_provider,
        num_threads=args.threads,
        sample_rate=samplerate,
        feature_dim=80,
        enable_endpoint_detection=True,
        rule1_min_trailing_silence=2.4,
        rule2_min_trailing_silence=1.2,
        rule3_min_utterance_length=20,  # it essentially disables this rule
    )
    return recognizer


def create_sensevoice(samplerate: int, args) -> sherpa_onnx.OfflineRecognizer:
    d = os.path.join(args.models_root,
                     'sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17')

    if not os.path.exists(d):
        raise ValueError(f"asr: model not found {d}")

    recognizer = sherpa_onnx.OfflineRecognizer.from_sense_voice(
        model=os.path.join(d, 'model.onnx'),
        tokens=os.path.join(d, 'tokens.txt'),
        num_threads=args.threads,
        sample_rate=samplerate,
        use_itn=True,
        debug=0,
        language=args.asr_lang,
    )
    return recognizer


def create_paraformer_trilingual(samplerate: int, args) -> sherpa_onnx.OnlineRecognizer:
    d = os.path.join(
        args.models_root, 'sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20')
    if not os.path.exists(d):
        raise ValueError(f"asr: model not found {d}")

    recognizer = sherpa_onnx.OfflineRecognizer.from_paraformer(
        paraformer=os.path.join(d, 'model.onnx'),
        tokens=os.path.join(d, 'tokens.txt'),
        num_threads=args.threads,
        sample_rate=samplerate,
        debug=0,
        provider=args.asr_provider,
    )
    return recognizer


def create_paraformer_en(samplerate: int, args) -> sherpa_onnx.OnlineRecognizer:
    d = os.path.join(
        args.models_root, 'sherpa-onnx-paraformer-en')
    if not os.path.exists(d):
        raise ValueError(f"asr: model not found {d}")

    recognizer = sherpa_onnx.OfflineRecognizer.from_paraformer(
        paraformer=os.path.join(d, 'model.onnx'),
        tokens=os.path.join(d, 'tokens.txt'),
        num_threads=args.threads,
        sample_rate=samplerate,
        use_itn=True,
        debug=0,
        provider=args.asr_provider,
    )
    return recognizer


def load_asr_engine(samplerate: int, args) -> sherpa_onnx.OnlineRecognizer:
    cache_engine = _asr_engines.get(args.asr_model)
    if cache_engine:
        return cache_engine
    st = time.time()
    if args.asr_model == 'zipformer-bilingual':
        cache_engine = create_zipformer(samplerate, args)
    elif args.asr_model == 'sensevoice':
        cache_engine = create_sensevoice(samplerate, args)
        _asr_engines['vad'] = load_vad_engine(samplerate, args)
    elif args.asr_model == 'paraformer-trilingual':
        cache_engine = create_paraformer_trilingual(samplerate, args)
        _asr_engines['vad'] = load_vad_engine(samplerate, args)
    elif args.asr_model == 'paraformer-en':
        cache_engine = create_paraformer_en(samplerate, args)
        _asr_engines['vad'] = load_vad_engine(samplerate, args)
    else:
        raise ValueError(f"asr: unknown model {args.asr_model}")
    _asr_engines[args.asr_model] = cache_engine
    logger.info(f"asr: engine loaded in {time.time() - st:.2f}s")
    return cache_engine


def load_vad_engine(samplerate: int, args, min_silence_duration: float = 0.25, buffer_size_in_seconds: int = 1000) -> sherpa_onnx.VoiceActivityDetector:
    config = sherpa_onnx.VadModelConfig()
    d = os.path.join(args.models_root, 'silero_vad')
    if not os.path.exists(d):
        raise ValueError(f"vad: model not found {d}")

    config.silero_vad.model = os.path.join(d, 'silero_vad.onnx')
    # 输出config.silero_vad可以设置的值
    print(dir(config))
    print(dir(config.silero_vad))
    # 当检测到语音结束后，会等待的静音时间
    # config.silero_vad.min_silence_duration = 1
    # 如果检测到的语音片段长度小于这个值，则该语音片段会被丢弃
    config.silero_vad.min_speech_duration = 0.05
    config.silero_vad.window_size = 512 
    # 低于该值的概率被认为是静音或背景噪音
    config.silero_vad.threshold = 0.2
    config.sample_rate = samplerate
    config.provider = args.asr_provider
    config.num_threads = args.threads

    #  'min_silence_duration', 'min_speech_duration', 'model', 'threshold', 'validate', 'window_size'
    # config.silero_vad.min_speech_duration = 0.25  # seconds

    vad = sherpa_onnx.VoiceActivityDetector(
        config,
        buffer_size_in_seconds=buffer_size_in_seconds)
    return vad

def load_vad_engine_self(samplerate: int, asr_provider, min_silence_duration: float = 0.25, buffer_size_in_seconds: int = 1000) -> sherpa_onnx.VoiceActivityDetector:
    config = sherpa_onnx.VadModelConfig()
    d = os.path.join('./models', 'silero_vad')
    if not os.path.exists(d):
        raise ValueError(f"vad: model not found {d}")

    config.silero_vad.model = os.path.join(d, 'silero_vad.onnx')
    # 输出config.silero_vad可以设置的值
    print(dir(config))
    print(dir(config.silero_vad))
    # 当检测到语音结束后，会等待的静音时间
    config.silero_vad.min_silence_duration = 1
    # 如果检测到的语音片段长度小于这个值，则该语音片段会被丢弃
    config.silero_vad.min_speech_duration = 0.05

    # 低于该值的概率被认为是静音或背景噪音
    config.silero_vad.threshold = 0.2
    config.sample_rate = samplerate
    config.provider =asr_provider
    config.num_threads = 1
    
    #  'min_silence_duration', 'min_speech_duration', 'model', 'threshold', 'validate', 'window_size'
    # config.silero_vad.min_speech_duration = 0.25  # seconds

    vad = sherpa_onnx.VoiceActivityDetector(
        config,
        buffer_size_in_seconds=buffer_size_in_seconds)
    return vad


async def start_asr_stream(samplerate: int, args) -> ASRStream:
    """
    Start a ASR stream
    """
    stream = ASRStream(load_asr_engine(samplerate, args), samplerate)
    await stream.start()
    return stream

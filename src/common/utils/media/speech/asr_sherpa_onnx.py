import sherpa_onnx
import os
from pathlib import Path
class ASRStream:
    
    
    def set_recognizer(
        samplerate: int = 16000, models_root:str="", lang="zh", threads=2,model_type="sensevoice"
    ) -> sherpa_onnx.OfflineRecognizer:
        path_root  = Path(models_root)
        


        
        if not os.path.exists(d):
            raise ValueError(f"asr: model not found {d}")

        if model_type == "sensevoice":
            model_dir = models_root/"sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17
            model_path = os.path.join(d, "model.onnx")
            tokens_path = os.path.join(d, "tokens.txt")
            recognizer = sherpa_onnx.OfflineRecognizer.from_sense_voice(
                model=model_path,
                tokens=tokens_path,
                num_threads=threads,
                sample_rate=samplerate,
                use_itn=True,
                debug=0,
                language=lang,
            )
        elif model_type == "paraformer":
            recognizer = sherpa_onnx.OfflineRecognizer.from_paraformer(
            model=model_path,
            tokens=tokens_path,
            num_threads=threads,
            sample_rate=samplerate,
            debug=0,
            provider='cpu',
            )
        elif model_type == "zipformer_stream":
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


    def set_vad(samplerate: int, args, min_silence_duration: float = 0.25, buffer_size_in_seconds: int = 100) -> sherpa_onnx.VoiceActivityDetector:
        config = sherpa_onnx.VadModelConfig()
        d = os.path.join(args.models_root, 'silero_vad')
        if not os.path.exists(d):
            raise ValueError(f"vad: model not found {d}")

        config.silero_vad.model = os.path.join(d, 'silero_vad.onnx')
        config.silero_vad.min_silence_duration = min_silence_duration
        config.sample_rate = samplerate
        config.provider = args.asr_provider
        config.num_threads = args.threads

        vad = sherpa_onnx.VoiceActivityDetector(
            config,
            buffer_size_in_seconds=buffer_size_in_seconds)
        return vad

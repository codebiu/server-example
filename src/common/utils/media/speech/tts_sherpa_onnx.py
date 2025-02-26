import sherpa_onnx
from pathlib import Path

class TTSSherpaOnnx:
    
    def set_recognizer(
        samplerate: int = 16000, models_root:str="", lang="zh", num_threads=2,rule_fsts_list =[]
    ) -> sherpa_onnx.OfflineRecognizer:
        models_root_path  = Path(models_root)
        
        model_dir = os.path.join(model_root, name)
        for f in cfg.get('rule_fsts', ''):
            fsts.append(os.path.join(model_dir, f))
        tts_rule_fsts = ','.join(fsts) if fsts else ''
        
        model_config = sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=os.path.join(model_dir, cfg['model']),
                lexicon=os.path.join(model_dir, cfg['lexicon']),
                dict_dir=os.path.join(model_dir, cfg['dict_dir']),
                tokens=os.path.join(model_dir, cfg['tokens']),
            ),
            provider=provider,
            debug=0,
            num_threads=num_threads,
        )
        tts_config = sherpa_onnx.OfflineTtsConfig(
            model=model_config,
            rule_fsts=tts_rule_fsts,
            max_num_sentences=20)

        cache_engine = sherpa_onnx.OfflineTts(tts_config)
        
        return cache_engine
    

if __name__ == "__main__":
    model_dir = 'sherpa-onnx-vits-zh-ll'
    model_name= 'model.onnx'
    lexicon = 'lexicon.txt',
    dict_dir = 'dict'
    tokens = 'tokens.txt'
    rule_fsts =  ['phone.fst', 'date.fst', 'number.fst'],
    samplerate = 16000
    threads = 1
import torch
import logging
from pathlib import Path
from typing import Optional, Union, List
import numpy as np
from tortoise.api import TextToSpeech

logger = logging.getLogger(__name__)

class EnhancedTTSEngine:
    """محرك تحويل النص إلى صوت المحسن"""
    
    def __init__(self, config: Optional[dict] = None):
        """تهيئة محرك TTS"""
        self.config = config or {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing TTS Engine on {self.device}")
        
        try:
            # محاولة تحميل DeepSpeed
            try:
                import deepspeed
                use_deepspeed = self.config.get('use_deepspeed', True)
                logger.info("DeepSpeed is available and will be used")
            except ImportError:
                use_deepspeed = False
                logger.warning("DeepSpeed not available - falling back to standard mode")
            
            # تهيئة نموذج Tortoise-TTS مع إعدادات محسنة
            self.tts = TextToSpeech(
                use_deepspeed=use_deepspeed,
                kv_cache=self.config.get('kv_cache', True),
                half=self.config.get('half', True),
                device=self.device
            )
            
            # تحميل الأصوات المدمجة
            self.available_voices = self._load_bundled_voices()
            logger.info("تم تهيئة النموذج بنجاح")
            
        except Exception as e:
            logger.error(f"فشل في تهيئة محرك TTS: {e}")
            raise

    def _load_bundled_voices(self) -> List[str]:
        """تحميل الأصوات المدمجة مع النموذج"""
        try:
            from tortoise.utils.audio import load_voices
            return load_voices()
        except Exception as e:
            logger.error(f"خطأ في تحميل الأصوات المدمجة: {e}")
            return []

    def generate(
        self,
        text: str,
        voice_file: Optional[str] = None,
        emotion: str = "طبيعي",
        speed: float = 1.0,
        quality: str = "عادية"
    ) -> np.ndarray:
        """توليد الصوت من النص"""
        try:
            # تحميل الصوت المرجعي إذا تم تحديده
            voice_samples = None
            if voice_file:
                voice_samples = self._load_voice(voice_file)
            
            # تحويل الجودة إلى عدد التكرارات
            num_samples = {
                "سريعة": 1,
                "عادية": 2,
                "عالية": 4
            }.get(quality, 2)
            
            # استدعاء Tortoise TTS
            gen_audio = self.tts.tts(
                text=text,
                voice_samples=voice_samples,
                k=num_samples,
                use_deterministic_seed=True,
                cvvp_amount=0.0
            )
            
            # معالجة الناتج
            if isinstance(gen_audio, list):
                audio_data = gen_audio[0]
            else:
                audio_data = gen_audio
                
            if isinstance(audio_data, torch.Tensor):
                audio_data = audio_data.detach().cpu().numpy()
            
            # إزالة الأبعاد الزائدة
            audio_data = np.squeeze(audio_data)
            
            # تطبيع القيم
            audio_data = np.clip(audio_data, -1.0, 1.0)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"خطأ في توليد الصوت: {e}")
            raise

    def _load_voice(self, voice_path: Union[str, Path]) -> Optional[torch.Tensor]:
        """تحميل ملف صوت مرجعي"""
        try:
            from tortoise.utils.audio import load_voice
            return load_voice(str(voice_path))
        except Exception as e:
            logger.error(f"خطأ في تحميل الصوت المرجعي '{voice_path}': {e}")
            return None

    def cleanup(self):
        """تنظيف الموارد"""
        try:
            if hasattr(self, 'tts'):
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
        except Exception as e:
            logger.error(f"خطأ في تنظيف موارد المحرك: {e}")
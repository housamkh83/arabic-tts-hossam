import logging
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)

class AudioProcessor:
    """معالج الصوت"""
    
    def __init__(self, config: dict = None):
        """تهيئة معالج الصوت"""
        self.config = config or {}
        self.sample_rate = self.config.get('sample_rate', 24000)
    
    def process_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """معالجة الصوت"""
        try:
            # التأكد من أن البيانات من نوع float32
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # تطبيع مستوى الصوت
            max_val = np.abs(audio_data).max()
            if max_val > 0:
                audio_data = audio_data / max_val
            
            return audio_data
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الصوت: {e}")
            raise
    
    def save_audio(self, audio_data: np.ndarray, path: Union[str, Path]) -> None:
        """حفظ الصوت في ملف"""
        try:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # التأكد من أن البيانات صالحة للحفظ
            if not isinstance(audio_data, np.ndarray):
                raise ValueError("بيانات الصوت يجب أن تكون من نوع numpy array")
            
            # حفظ الملف
            sf.write(str(path), audio_data, self.sample_rate)
            logger.info(f"تم حفظ الصوت في: {path}")
            
        except Exception as e:
            logger.error(f"خطأ في حفظ الصوت: {e}")
            raise
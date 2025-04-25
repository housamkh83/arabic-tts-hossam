# interface/tts_interface.py

import logging
import time
from pathlib import Path
from typing import Optional, Tuple, Dict
from core.text_processor import ArabicTextProcessor
from core.audio_processor import AudioProcessor
from core.tts_engine import EnhancedTTSEngine

logger = logging.getLogger(__name__)

class TTSInterface:
    """الواجهة الوسيطة بين واجهة المستخدم ومحرك TTS"""
    
    def __init__(self, config: dict, directories: dict):
        """تهيئة الواجهة الوسيطة"""
        logger.info("Initializing TTS Interface Logic...")
        
        try:
            self.config = config or {}
            self.directories = directories
            
            # تهيئة المكونات الأساسية
            self.text_processor = ArabicTextProcessor()
            self.audio_processor = AudioProcessor(config=self.config.get('audio', {}))
            
            # تهيئة محرك TTS مع محاولات إعادة
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    self.tts_engine = EnhancedTTSEngine(config=self.config.get('tts_engine', {}))
                    if self.tts_engine is not None:
                        logger.info("TTS Engine initialized successfully")
                        break
                    retry_count += 1
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"TTS Engine initialization attempt {retry_count} failed: {e}")
                        time.sleep(1)  # انتظر قليلاً قبل المحاولة مرة أخرى
                    else:
                        raise RuntimeError(f"Failed to initialize TTS Engine after {max_retries} attempts: {e}")

            if self.tts_engine is None:
                raise RuntimeError("TTS Engine initialization failed - engine is None")
                
            logger.info("TTS Interface Logic initialized successfully.")
            
        except Exception as e:
            logger.critical(f"Failed to initialize TTS Interface: {e}")
            raise RuntimeError(f"TTS Interface initialization failed: {e}") from e

    def process_request(
        self,
        text: str,
        voice_filename: Optional[str] = None,
        emotion: str = "طبيعي",
        speed: float = 1.0,
        quality: str = "عادية",
        progress: Optional[callable] = None
    ) -> Tuple[Optional[str], str]:
        """معالجة طلب تحويل النص إلى صوت"""
        try:
            logger.info(f"Processing TTS request: voice='{voice_filename}', quality='{quality}', speed={speed}, emotion='{emotion}'")
            
            # التحقق من تهيئة المحرك
            if self.tts_engine is None:
                error_msg = "TTS Engine is not initialized"
                logger.error(error_msg)
                return None, error_msg
            
            if progress:
                progress(0.1, "معالجة النص...")
            
            # معالجة النص العربي
            processed_text = self.text_processor.process(text)
            if not processed_text:
                return None, "النص فارغ أو غير صالح"
            
            if progress:
                progress(0.3, "توليد الصوت...")
                
            # توليد الصوت
            audio_data = self.tts_engine.generate(
                text=processed_text,
                voice_file=voice_filename,
                emotion=emotion,
                speed=speed,
                quality=quality
            )
            
            if progress:
                progress(0.8, "معالجة وحفظ الصوت...")
            
            # معالجة وحفظ الصوت
            output_filename = f"tts_{int(time.time())}.wav"
            output_path = Path(self.directories['output']) / output_filename
            
            audio_data = self.audio_processor.process_audio(audio_data)
            self.audio_processor.save_audio(audio_data, output_path)
            
            if progress:
                progress(1.0, "اكتمل!")
                
            return str(output_path), "تم إنشاء الصوت بنجاح"
            
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            return None, f"حدث خطأ: {str(e)}"
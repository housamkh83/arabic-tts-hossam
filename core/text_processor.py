import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

class ArabicTextProcessor:
    """معالج النص العربي"""
    
    def __init__(self):
        """تهيئة المعالج"""
        self.ar_to_en = {
            'ا': 'a', 'ب': 'b', 'ت': 't', 'ث': 'th',
            'ج': 'j', 'ح': 'H', 'خ': 'kh', 'د': 'd',
            'ذ': 'th', 'ر': 'r', 'ز': 'z', 'س': 's',
            'ش': 'sh', 'ص': 'S', 'ض': 'D', 'ط': 'T',
            'ظ': 'Z', 'ع': '3', 'غ': 'gh', 'ف': 'f',
            'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm',
            'ن': 'n', 'ه': 'h', 'و': 'w', 'ي': 'y',
            'ة': 'h', 'ء': '2', 'ؤ': '2', 'ئ': '2',
            'أ': '2', 'إ': '2', 'آ': '2aa',
            'َ': 'a', 'ُ': 'u', 'ِ': 'i',
            'ً': 'an', 'ٌ': 'un', 'ٍ': 'in',
            'ّ': '~', 'ْ': ''
        }
        logger.debug("Arabic text processor initialized")

    def process(self, text: str) -> str:
        """
        معالجة النص العربي وتحويله إلى نص لاتيني
        
        Args:
            text: النص العربي المدخل
            
        Returns:
            str: النص المعالج بالحروف اللاتينية
        """
        if not text or not isinstance(text, str):
            return ""
            
        try:
            # تنظيف النص
            text = self._clean_text(text)
            
            # تقسيم إلى جمل
            sentences = self._split_sentences(text)
            
            # معالجة كل جملة وتجميعها في نص واحد
            processed = []
            for sentence in sentences:
                if sentence := sentence.strip():
                    transliterated = self._transliterate(sentence)
                    processed.append(transliterated)
            
            # دمج الجمل مع فواصل مناسبة
            return " . ".join(processed)
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            return ""

    def _clean_text(self, text: str) -> str:
        """تنظيف النص من العلامات غير المرغوبة"""
        text = re.sub('ـ', '', text)
        text = text.replace('ى', 'ي').replace('ة', 'ه')
        return text.strip()

    def _split_sentences(self, text: str) -> list:
        """تقسيم النص إلى جمل"""
        sentences = re.split('[.!؟\n]', text)
        return [s.strip() for s in sentences if s.strip()]

    def _transliterate(self, text: str) -> str:
        """تحويل النص العربي إلى أحرف لاتينية"""
        result = []
        for char in text:
            if char in self.ar_to_en:
                result.append(self.ar_to_en[char])
            elif char.isspace():
                result.append(' ')
        return ''.join(result)
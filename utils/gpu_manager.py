import torch
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class GPUManager:
    """إدارة موارد GPU"""
    
    _instance = None
    _is_initialized = False

    @classmethod
    def setup(cls) -> bool:
        """
        إعداد وفحص توفر GPU
        
        Returns:
            bool: True إذا كان GPU متوفر وتم الإعداد بنجاح
        """
        try:
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0) if device_count > 0 else "Unknown"
                logger.info(f"GPU is available: {device_name}")
                logger.info(f"Number of devices: {device_count}")
                logger.info(f"CUDA version: {torch.version.cuda}")
                
                # محاولة تهيئة CUDA
                torch.cuda.init()
                
                # تنظيف الذاكرة المبدئي
                torch.cuda.empty_cache()
                
                cls._is_initialized = True
                return True
            else:
                logger.warning("No GPU detected. Running on CPU mode.")
                return False
                
        except Exception as e:
            logger.error(f"Error during GPU setup: {e}")
            return False

    @staticmethod
    def is_available() -> bool:
        """التحقق من توفر GPU"""
        return torch.cuda.is_available()

    @staticmethod
    @contextmanager
    def cuda_memory_management():
        """سياق لإدارة ذاكرة CUDA"""
        try:
            torch.cuda.empty_cache()
            yield
        finally:
            torch.cuda.empty_cache()

    @staticmethod
    def get_memory_info() -> dict:
        """الحصول على معلومات الذاكرة"""
        if not torch.cuda.is_available():
            return {"error": "GPU غير متوفر"}
            
        return {
            "allocated": torch.cuda.memory_allocated(),
            "reserved": torch.cuda.memory_reserved(),
            "max_allocated": torch.cuda.max_memory_allocated()
        }

    @staticmethod
    def clear():
        """تنظيف ذاكرة GPU"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.debug("GPU memory cleared")
import logging
from contextlib import contextmanager
import torch
from .gpu_manager import GPUManager

logger = logging.getLogger(__name__)

class ContextManager:
    """مدير السياق للعمليات المختلفة"""

    @staticmethod
    @contextmanager
    def resource_management():
        """سياق لإدارة الموارد العامة"""
        try:
            yield
        finally:
            # تنظيف الموارد
            torch.cuda.empty_cache()
            
    @staticmethod
    @contextmanager
    def error_handling(operation_name: str):
        """
        سياق لمعالجة الأخطاء
        
        Args:
            operation_name: اسم العملية للتسجيل
        """
        try:
            logger.debug(f"بدء العملية: {operation_name}")
            yield
            logger.debug(f"اكتملت العملية: {operation_name}")
        except Exception as e:
            logger.error(f"خطأ في العملية {operation_name}: {e}", exc_info=True)
            raise

    @staticmethod
    @contextmanager
    def performance_logging(operation_name: str):
        """
        سياق لتسجيل أداء العمليات
        
        Args:
            operation_name: اسم العملية للتسجيل
        """
        import time
        start_time = time.time()
        try:
            yield
        finally:
            elapsed_time = time.time() - start_time
            logger.info(f"استغرقت العملية {operation_name}: {elapsed_time:.2f} ثانية")
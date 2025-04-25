# utils/logger_setup.py
import logging
import yaml
from pathlib import Path
from typing import Optional, Dict

# تعريف المسارات الافتراضية
DEFAULT_CONFIG_PATH = "config.yaml"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE = "logs/app.log"

def setup_logging(config_path: str = DEFAULT_CONFIG_PATH) -> Optional[dict]:
    """
    إعداد نظام التسجيل وتحميل الإعدادات
    
    Args:
        config_path: مسار ملف الإعدادات
        
    Returns:
        dict: قاموس الإعدادات المحملة أو None في حالة الفشل
    """
    # تحميل الإعدادات
    config = _load_config(config_path)
    log_config = config.get('logging', {}) if config else {}
    
    try:
        # إنشاء مجلد السجلات
        log_file = log_config.get('file', DEFAULT_LOG_FILE)
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # إعداد المُسجل الرئيسي
        root_logger = logging.getLogger()
        root_logger.setLevel(log_config.get('level', DEFAULT_LOG_LEVEL))

        # تنسيق السجلات
        formatter = logging.Formatter(
            log_config.get('format', DEFAULT_LOG_FORMAT)
        )

        # إضافة معالج الملف
        file_handler = logging.FileHandler(
            log_file,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)

        # إضافة معالج وحدة التحكم
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # حذف المعالجات القديمة
        root_logger.handlers.clear()

        # إضافة المعالجات الجديدة
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        logger = logging.getLogger(__name__)
        logger.debug("Logging setup complete")
        
        return config

    except Exception as e:
        print(f"Error setting up logging: {e}")
        return None

def _load_config(config_path: str) -> Optional[dict]:
    """
    تحميل ملف الإعدادات
    
    Args:
        config_path: مسار ملف الإعدادات
        
    Returns:
        dict: قاموس الإعدادات أو None في حالة الفشل
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}, using defaults")
        return None
    except Exception as e:
        print(f"Error loading config: {e}")
        return None
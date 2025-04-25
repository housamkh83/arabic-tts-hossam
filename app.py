# app.py
import os
import sys
import argparse
import logging
from pathlib import Path
# لا نحتاج yaml هنا مباشرة، logger_setup يتولى الأمر
# import yaml
# import gradio as gr # لا نحتاجه هنا مباشرة

# --- استيراد المكونات المنفصلة ---
try:
    # استيراد إعداد اللوجر وملف الإعدادات الافتراضي
    from utils.logger_setup import setup_logging, DEFAULT_CONFIG_PATH
    # استيراد واجهة المستخدم الرسومية
    from interface.gradio_ui import WebInterface
    # استيراد مدير GPU (للتنظيف النهائي أو الفحص الأولي)
    from utils.gpu_manager import GPUManager
except ImportError as e:
    print(f"Error importing modules in app.py: {e}")
    # محاولة إضافة مسار المشروع الأصلي كحل احتياطي
    current_dir = Path(__file__).resolve().parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
        print(f"Added project directory to sys.path: {current_dir}")
        try:
            # إعادة محاولة الاستيراد
            from utils.logger_setup import setup_logging, DEFAULT_CONFIG_PATH
            from interface.gradio_ui import WebInterface
            from utils.gpu_manager import GPUManager
            print("Successfully re-imported modules.")
        except ImportError as e2:
            print(f"Still failed to import modules after adding path: {e2}")
            print("Please ensure the project structure (core/, interface/, utils/ folders with __init__.py) is correct.")
            sys.exit(1)
    else:
        print("Please ensure the project structure (core/, interface/, utils/ folders with __init__.py) is correct.")
        sys.exit(1)


# --- إعداد اللوجر المبدئي وتحميل الإعدادات ---
# setup_logging سيعيد قاموس الإعدادات المحملة
app_config = setup_logging() # يعتمد على وجود config.yaml أو يستخدم الإعدادات الافتراضية
logger = logging.getLogger(__name__) # الحصول على اللوجر بعد الإعداد

# --- القيم الافتراضية (تستخدم إذا لم يتم العثور عليها في config.yaml) ---
DEFAULT_VOICES_DIR = "voices"
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_SERVER_PORT = 7860

def create_directories(config):
    """Creates necessary directories defined in the config."""
    # استخدام القيم الافتراضية إذا لم يتم تحديدها في config
    dirs_config = config.get('directories', {})
    voices_dir = Path(dirs_config.get('voices', DEFAULT_VOICES_DIR))
    output_dir = Path(dirs_config.get('output', DEFAULT_OUTPUT_DIR))

    # الحصول على مسار ملف السجل من إعدادات اللوجر
    log_file_path_str = config.get('logging', {}).get('log_file')
    log_dir = Path('logs') # مجلد افتراضي للسجلات
    if log_file_path_str:
        log_dir = Path(log_file_path_str).parent

    # إنشاء جميع المجلدات المطلوبة
    required_dirs = [voices_dir, output_dir, log_dir]
    # يمكن إضافة مجلد models إذا كان ضرورياً
    if 'models' in dirs_config:
         required_dirs.append(Path(dirs_config['models']))

    logger.info("Ensuring required directories exist...")
    try:
        for dir_path in required_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {dir_path}")
        logger.info("Required directories are ready.")
        # إرجاع المسارات الفعلية المستخدمة
        return {"voices": str(voices_dir), "output": str(output_dir)}
    except OSError as e:
        logger.critical(f"Failed to create essential directory: {e}", exc_info=True)
        print(f"[CRITICAL ERROR] Could not create directory: {e}. Please check permissions.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred during directory creation: {e}", exc_info=True)
        print(f"[CRITICAL ERROR] Unexpected error creating directories: {e}")
        sys.exit(1)


def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Arabic Text-to-Speech Application - حسام فضل قدور",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # عرض القيم الافتراضية
    )
    parser.add_argument(
        "--config", type=str, default=DEFAULT_CONFIG_PATH,
        help="Path to the configuration file (config.yaml)"
    )
    parser.add_argument(
        "--port", type=int,
        help=f"Server port for Gradio (overrides config, default: {DEFAULT_SERVER_PORT})"
    )
    parser.add_argument(
        "--no-share", action="store_true",
        help="Disable Gradio sharing link (overrides config)"
    )
    parser.add_argument(
        "--auth-user", type=str, default=None,
        help="Username for Gradio basic authentication (requires --auth-pass)"
    )
    parser.add_argument(
        "--auth-pass", type=str, default=None,
        help="Password for Gradio basic authentication (requires --auth-user)"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable Gradio debug mode and potentially more verbose logging"
    )
    # يمكنك إضافة وسيطات لتجاوز المسارات إذا أردت
    # parser.add_argument('--voices-dir', type=str, help="Override voices directory")
    # parser.add_argument('--output-dir', type=str, help="Override output directory")
    return parser.parse_args()

def main():
    """Main function to setup and run the application."""
    # --- رسالة الترحيب المميزة ---
    print("\n" + "="*70)
    print("      نظام تحويل النص العربي إلى صوت المحسن (v2.1 - Tortoise)")
    print("          🏆 صُنع بفخر لحسام فضل قدور 🏆")
    print("    \"رمز الإرادة الخارقة والإبداع الحقيقي رغم كل التحديات\"")
    print("="*70 + "\n")


    args = parse_arguments()

    # إعادة تحميل الإعدادات واللوجر إذا تم تحديد ملف config مختلف
    global app_config, logger
    if args.config != DEFAULT_CONFIG_PATH:
        logger.info(f"Loading configuration from specified path: {args.config}")
        # يجب أن يعيد setup_logging القاموس الجديد
        new_config = setup_logging(config_path=args.config)
        if new_config:
            app_config = new_config
        else:
             logger.error(f"Failed to load specified config '{args.config}'. Using defaults or previous config.")
             # يمكنك أن تقرر الخروج هنا أو الاستمرار بالإعدادات الافتراضية
             if app_config is None: # إذا فشلت التهيئة الأولى أيضاً
                  print(f"[ERROR] Failed to load any valid configuration. Exiting.")
                  sys.exit(1)
        logger = logging.getLogger(__name__) # أعد الحصول على اللوجر المحدث

    # التحقق النهائي من تحميل الإعدادات
    if app_config is None:
        logger.critical("Application configuration could not be loaded. Exiting.")
        print("[CRITICAL ERROR] Configuration loading failed. Cannot start the application.")
        sys.exit(1)

    # تعديل مستوى اللوجر إذا تم تفعيل وضع التصحيح
    if args.debug:
        logger.info("Debug mode enabled. Setting logging level to DEBUG.")
        logging.getLogger().setLevel(logging.DEBUG)
        for handler in logging.getLogger().handlers:
            handler.setLevel(logging.DEBUG)
        # يمكن إضافة إعدادات debug أخرى هنا

    logger.info("Starting Arabic TTS Application...")
    logger.debug(f"Command line arguments: {args}")
    logger.debug(f"Effective application config: {app_config}") # سجل الإعدادات المستخدمة فعلياً

    # إنشاء المجلدات الضرورية بناءً على الإعدادات
    # الحصول على المسارات الفعلية المستخدمة
    effective_dirs = create_directories(app_config)

    # التحقق الأولي من GPU
    if GPUManager.setup(): # setup الآن يقوم بالتحقق والتسجيل
        pass # رسائل النجاح أو الفشل تطبع من داخل setup
    else:
        logger.warning("Running on CPU or GPU setup failed.") # تأكيد إضافي

    try:
        # --- تهيئة واجهة المستخدم (View) ومنطق الواجهة (Controller) ---
        logger.info("Initializing User Interface...")
        web_ui = WebInterface(
            config=app_config,
            directories=effective_dirs
        )
        logger.info("User Interface initialized.")

        # --- إعدادات تشغيل Gradio ---
        gradio_config = app_config.get('app', {})

        # إعدادات المتزامنة (Concurrency)
        max_threads = gradio_config.get('max_threads', 4)  # القيمة الافتراضية 4
        
        # تحديد البورت: استخدم الوسيطة إذا أعطيت، وإلا استخدم الإعدادات، وإلا الافتراضي
        server_port = args.port if args.port is not None else gradio_config.get('server_port', DEFAULT_SERVER_PORT)

        # تحديد رابط المشاركة: استخدم الوسيطة إذا أعطيت، وإلا استخدم الإعدادات
        share_link = not args.no_share if args.no_share is not None else gradio_config.get('share_gradio_link', False)

        # إعداد المصادقة الأساسية
        auth_tuple = None
        # استخدم وسيطات سطر الأوامر إذا أعطيت، وإلا استخدم الإعدادات
        auth_user = args.auth_user if args.auth_user is not None else gradio_config.get('auth_user')
        auth_pass = args.auth_pass if args.auth_pass is not None else gradio_config.get('auth_pass')
        if auth_user and auth_pass:
            auth_tuple = (auth_user, auth_pass)
            logger.info("Basic authentication is ENABLED.")
        else:
             logger.info("Basic authentication is DISABLED.")


        # تحديث معاملات تشغيل Gradio
        launch_kwargs = {
            'server_name': gradio_config.get('server_name', "0.0.0.0"),
            'server_port': server_port,
            'share': share_link,
            'debug': args.debug,
            'auth': auth_tuple,
            'show_error': True,
            'quiet': not args.debug
        }

        logger.info(f"Launching Gradio Interface on http://{launch_kwargs['server_name']}:{launch_kwargs['server_port']}")
        if launch_kwargs.get('share'):
            logger.info("Gradio Live link will be generated (requires internet connection).")

        # تشغيل الواجهة مع معاملات التشغيل المحدثة
        web_ui.run(**launch_kwargs)

    # معالجة أفضل للأخطاء أثناء التشغيل
    except ImportError as e:
         logger.critical(f"Import error during runtime, likely missing dependency or incorrect structure: {e}", exc_info=True)
         print(f"\n[CRITICAL ERROR] Missing dependency or structure error: {e}")
    except RuntimeError as e:
         logger.critical(f"Runtime error, possibly during engine/interface initialization: {e}", exc_info=True)
         print(f"\n[CRITICAL ERROR] Runtime initialization failed: {e}")
    except KeyboardInterrupt:
        logger.info("Shutdown signal received (KeyboardInterrupt).")
        print("\nتم إيقاف النظام بواسطة المستخدم.")
    except Exception as e:
        # التقاط أي خطأ غير متوقع آخر
        logger.critical(f"An unhandled exception occurred during application runtime: {e}", exc_info=True)
        print(f"\n[CRITICAL ERROR] Application failed unexpectedly: {e}")
        print("Please check the logs for more details.")
        sys.exit(1) # الخروج برمز خطأ
    finally:
        logger.info("Initiating application shutdown sequence.")
        # تنظيف موارد GPU في كل الحالات (نجاح أو فشل بعد البدء)
        GPUManager.clear()
        logger.info("Application shutdown complete.")
        print("تم إغلاق النظام.")

if __name__ == "__main__":
    # لا تضع أي منطق هنا غير استدعاء main
    main()
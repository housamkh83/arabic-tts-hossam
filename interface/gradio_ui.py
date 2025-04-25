# interface/gradio_ui.py

import logging
import gradio as gr
from pathlib import Path
from typing import Optional, Tuple, List, Callable

from .tts_interface import TTSInterface

logger = logging.getLogger(__name__)

class WebInterface:
    """واجهة المستخدم الرسومية باستخدام Gradio"""
    
    def __init__(self, config: Optional[dict] = None, directories: Optional[dict] = None):
        """تهيئة واجهة المستخدم"""
        self.config = config or {}
        self.directories = directories or {
            'voices': 'voices',
            'output': 'output'
        }
        self.interface = None
        self.tts = TTSInterface(
            config=self.config,
            directories=self.directories
        )
        self._create_interface()
    
    def _create_interface(self):
        """إنشاء واجهة Gradio"""
        try:
            with gr.Blocks(title="نظام تحويل النص العربي إلى صوت") as self.interface:
                gr.Markdown("""
                # نظام تحويل النص العربي إلى صوت 🗣️
                أدخل النص العربي المراد تحويله إلى صوت
                """)
                
                with gr.Row():
                    with gr.Column():
                        text_input = gr.Textbox(
                            label="النص العربي",
                            placeholder="اكتب النص هنا...",
                            lines=5
                        )
                        
                        with gr.Row():
                            voice_dropdown = gr.Dropdown(
                                choices=self._get_voice_files(),
                                label="اختر الصوت المرجعي"
                            )
                            emotion_dropdown = gr.Dropdown(
                                choices=["طبيعي", "سعيد", "حزين", "غاضب"],
                                label="النبرة",
                                value="طبيعي"
                            )
                        
                        with gr.Row():
                            speed_slider = gr.Slider(
                                minimum=0.5,
                                maximum=2.0,
                                value=1.0,
                                step=0.1,
                                label="سرعة النطق"
                            )
                            quality_dropdown = gr.Dropdown(
                                choices=["سريعة", "عادية", "عالية"],
                                label="جودة الصوت",
                                value="عادية"
                            )
                        
                        generate_btn = gr.Button("توليد الصوت ▶")
                    
                    with gr.Column():
                        audio_output = gr.Audio(label="الصوت الناتج")
                        status_text = gr.Textbox(
                            label="حالة العملية",
                            interactive=False
                        )

                def process_text(
                    text: str,
                    voice_file: str,
                    emotion: str,
                    speed: float,
                    quality: str,
                    progress: gr.Progress
                ) -> Tuple[Optional[str], str]:
                    """معالجة النص وتحويله إلى صوت"""
                    try:
                        return self.tts.process_request(
                            text=text,
                            voice_filename=voice_file,
                            emotion=emotion,
                            speed=speed,
                            quality=quality,
                            progress=progress
                        )
                    except Exception as e:
                        logger.error(f"خطأ في توليد الصوت: {e}", exc_info=True)
                        return None, f"حدث خطأ: {str(e)}"

                # ربط الأحداث
                generate_btn.click(
                    fn=process_text,
                    inputs=[
                        text_input,
                        voice_dropdown,
                        emotion_dropdown,
                        speed_slider,
                        quality_dropdown
                    ],
                    outputs=[audio_output, status_text]
                )
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء الواجهة: {e}", exc_info=True)
            raise

    def _get_voice_files(self) -> List[str]:
        """الحصول على قائمة ملفات الأصوات المتوفرة"""
        voices_dir = Path(self.directories['voices'])
        voices_dir.mkdir(exist_ok=True)
        return [f.name for f in voices_dir.glob("*.wav")] or ["default.wav"]

    def launch(self, **kwargs):
        """تشغيل الواجهة"""
        if self.interface:
            # تنقية وتعديل معاملات Gradio
            valid_params = {
                'server_name': kwargs.get('server_name', '0.0.0.0'),
                'server_port': kwargs.get('server_port', 7860),
                'share': kwargs.get('share', False),
                'debug': kwargs.get('debug', False),
                'auth': kwargs.get('auth'),
                'show_error': kwargs.get('show_error', True),
                'quiet': kwargs.get('quiet', True)
            }
            return self.interface.launch(**valid_params)
        else:
            raise RuntimeError("لم يتم إنشاء الواجهة بشكل صحيح")

    def run(self, **kwargs):
        """تشغيل الواجهة (اختصار لـ launch)"""
        return self.launch(**kwargs)
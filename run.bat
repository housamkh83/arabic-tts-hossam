call venv\Scripts\activate

:: [1] PyTorch من مصدر رسمي
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

:: [2] Tortoise-TTS من GitHub
pip install git+https://github.com/neonbjb/tortoise-tts.git

:: [3] مكتبات أساسية للواجهة
pip install gradio pyyaml

:: [4] باقي المتطلبات (بعد إزالة tortoise-tts منها)
pip install -r requirements.txt

:: [5] تشغيل البرنامج
python app.py

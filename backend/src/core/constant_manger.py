from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATE_DIR = BASE_DIR / "src" / "templates"

VOICE_DIR = "src/media/voices"

ESP32_URL = "http://192.168.1.50"
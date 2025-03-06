import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "hf.co/elyza/Llama-3-ELYZA-JP-8B-GGUF:latest")

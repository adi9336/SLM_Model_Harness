"""Configuration for the Two-Level Agent Harness."""
import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------- Tinker Cloud API (Qwen 8B)
# When provided, the Reasoner offloads inference to Qwen in the cloud via Tinker API
TINKER_API_KEY = os.getenv("TINKER_API_KEY", "")
TINKER_BASE_URL = os.getenv("TINKER_BASE_URL", "https://tinker.thinkingmachines.dev/services/tinker-prod/oai/api/v1")
TINKER_MODEL = os.getenv(
    "TINKER_MODEL",
    "tinker://5165c05b-e5bc-591b-99f4-d732ef85b72e:train:0/sampler_weights/final",
)

# ---------------------------------------------------------------------- Local Ollama Endpoint
# Used when running models 100% locally on localhost
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")

# Models
# Reasoner (decomposes task into atomic natural-language steps)
PRIORITY_MODEL = os.getenv("PRIORITY_MODEL", "qwen3:8b")
PRIORITY_TEMPERATURE = float(os.getenv("PRIORITY_TEMPERATURE", "0.1"))

# Formatter (xLAM: formats single atomic tool calls with exact arguments)
FORMATTER_MODEL = os.getenv("FORMATTER_MODEL", "xlam2:1b-fc-q4")
FORMATTER_TEMPERATURE = float(os.getenv("FORMATTER_TEMPERATURE", "0.0"))
FORMATTER_MODE = os.getenv("FORMATTER_MODE", "xlam")
FORMATTER_FALLBACK = bool(int(os.getenv("FORMATTER_FALLBACK", "1")))

# Execution limits & pacing
MAX_STEPS = int(os.getenv("MAX_STEPS", "12"))
DEMO_PACING_DELAY = float(os.getenv("DEMO_PACING_DELAY", "0.4"))

# Optional generic OpenAI-compatible alternative
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENCODE_SESSION = os.getenv("OPENCODE_SESSION", "slm-harness")

"""
Configuration management for Voice Cloning API
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Settings
    API_TITLE: str = "Voice Cloning API for AI Phone Agents"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1  # Keep at 1 for TTS model singleton

    # TTS Model Settings
    TTS_MODEL_NAME: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    TTS_DEVICE: str = "cuda"  # "cuda" or "cpu"
    TTS_USE_DEEPSPEED: bool = False  # Enable for faster inference

    # Audio Settings
    SAMPLE_RATE: int = 24000  # XTTS native rate
    TELEPHONY_SAMPLE_RATE: int = 8000  # Phone call standard
    AUDIO_FORMAT: str = "wav"  # Output format

    # Voice Library
    VOICES_DIR: Path = Path("api/voices")
    MAX_VOICE_SAMPLES: int = 100
    MIN_SAMPLE_DURATION: float = 3.0  # seconds
    MAX_SAMPLE_DURATION: float = 30.0  # seconds

    # Performance Settings
    ENABLE_CACHING: bool = True
    CACHE_DIR: Path = Path("api/cache")
    CACHE_MAX_SIZE_GB: float = 5.0

    # Natural Speech Settings
    ADD_NATURAL_PAUSES: bool = True
    ADD_BREATHING: bool = True
    BREATH_PROBABILITY: float = 0.15  # 15% chance of breath between sentences
    MICRO_PAUSE_DURATION: float = 0.15  # seconds

    # Telephony Optimization
    APPLY_TELEPHONY_FILTER: bool = True
    TELEPHONY_LOW_FREQ: int = 300  # Hz
    TELEPHONY_HIGH_FREQ: int = 3400  # Hz
    APPLY_COMPRESSION: bool = True
    COMPRESSION_THRESHOLD: float = -20.0  # dB

    # Streaming Settings
    STREAMING_ENABLED: bool = True
    CHUNK_SIZE_MS: int = 100  # milliseconds per chunk

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///api/voices.db"

    # Redis (for caching)
    REDIS_URL: Optional[str] = None
    REDIS_ENABLED: bool = False

    # Security
    API_KEY_ENABLED: bool = False
    API_KEY: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.VOICES_DIR.mkdir(parents=True, exist_ok=True)
settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)

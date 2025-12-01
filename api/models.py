"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime


class SpeakRequest(BaseModel):
    """Request model for text-to-speech synthesis"""

    text: str = Field(
        ...,
        description="Text to convert to speech",
        min_length=1,
        max_length=5000,
        example="Hi Sarah, I'm calling about your appointment tomorrow at 2 PM."
    )

    voice_id: str = Field(
        ...,
        description="Voice identifier to use for synthesis",
        example="professional_female_01"
    )

    context: Literal["greeting", "question", "empathy", "information", "closing", "neutral"] = Field(
        default="neutral",
        description="Conversation context for prosody adjustment"
    )

    emotion: Literal["neutral", "friendly", "concerned", "excited", "professional", "warm"] = Field(
        default="friendly",
        description="Emotional tone to apply"
    )

    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Speech speed multiplier (0.5-2.0)"
    )

    add_naturals: bool = Field(
        default=True,
        description="Add natural speech patterns (breathing, pauses, etc.)"
    )

    streaming: bool = Field(
        default=False,
        description="Enable streaming response for lower latency"
    )

    telephony_format: bool = Field(
        default=False,
        description="Convert to telephony format (8kHz μ-law)"
    )

    language: str = Field(
        default="en",
        description="Language code (en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja)"
    )


class SpeakResponse(BaseModel):
    """Response model for text-to-speech synthesis"""

    audio_url: Optional[str] = Field(
        None,
        description="URL to download generated audio (if not streaming)"
    )

    duration: float = Field(
        ...,
        description="Audio duration in seconds"
    )

    processing_time: float = Field(
        ...,
        description="Time taken to generate audio in seconds"
    )

    sample_rate: int = Field(
        ...,
        description="Audio sample rate in Hz"
    )

    format: str = Field(
        ...,
        description="Audio format (wav, mp3, etc.)"
    )

    real_time_factor: float = Field(
        ...,
        description="Processing time / audio duration (< 1.0 is real-time capable)"
    )


class VoiceCloneRequest(BaseModel):
    """Request model for cloning a new voice"""

    voice_id: str = Field(
        ...,
        description="Unique identifier for the voice",
        pattern="^[a-z0-9_-]+$",
        example="customer_service_female"
    )

    name: str = Field(
        ...,
        description="Human-readable name for the voice",
        example="Professional Female Voice"
    )

    description: Optional[str] = Field(
        None,
        description="Description of the voice characteristics",
        example="Warm, professional female voice ideal for customer service"
    )

    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorizing the voice",
        example=["female", "professional", "friendly"]
    )


class VoiceInfo(BaseModel):
    """Information about a cloned voice"""

    voice_id: str
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    sample_count: int = Field(..., description="Number of audio samples")
    total_duration: float = Field(..., description="Total duration of samples in seconds")
    created_at: datetime
    language: str = "en"
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class VoiceListResponse(BaseModel):
    """Response model for listing voices"""

    voices: List[VoiceInfo]
    total: int


class HealthResponse(BaseModel):
    """Health check response"""

    status: Literal["healthy", "unhealthy"]
    version: str
    model_loaded: bool
    device: str
    uptime_seconds: float


class MetricsResponse(BaseModel):
    """API metrics response"""

    total_requests: int
    total_audio_generated_seconds: float
    average_latency_ms: float
    average_rtf: float
    cache_hit_rate: float
    active_voices: int

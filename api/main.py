"""
Voice Cloning API for AI Phone Agents
FastAPI application with production-ready endpoints
"""
import io
import time
import logging
from pathlib import Path
from typing import Optional
import tempfile
import uuid

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Response
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import soundfile as sf
import numpy as np

from api.config import settings
from api.models import (
    SpeakRequest, SpeakResponse, VoiceCloneRequest,
    VoiceInfo, VoiceListResponse, HealthResponse, MetricsResponse
)
from api.tts_service import get_tts_service, AudioProcessor
from api.voice_manager import get_voice_library

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="""
    🎙️ **Voice Cloning API for Natural-Sounding AI Phone Agents**

    Transform text into human-like speech with voice cloning technology.
    Designed for AI phone systems (Vapi, Bland AI, Retell AI, etc.)

    ## Features
    - ✅ Fast voice cloning from 5-10 second samples
    - ✅ Real-time synthesis (<1.5s latency)
    - ✅ Natural speech patterns (pauses, breathing, prosody)
    - ✅ Telephony optimization (8kHz μ-law format)
    - ✅ Streaming support for low latency
    - ✅ Multi-language support (14+ languages)

    ## Endpoints
    - `/api/v1/speak` - Convert text to speech with voice cloning
    - `/api/v1/voices` - Manage voice library
    - `/api/v1/health` - Health check
    """,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Application state
app_start_time = time.time()
metrics = {
    "total_requests": 0,
    "total_audio_seconds": 0.0,
    "total_processing_time": 0.0,
    "cache_hits": 0,
    "cache_misses": 0
}


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("=" * 60)
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info("=" * 60)

    # Initialize TTS service
    try:
        tts = get_tts_service()
        logger.info(f"✓ TTS service initialized on {tts.device}")
    except Exception as e:
        logger.error(f"✗ Failed to initialize TTS service: {e}")
        raise

    # Initialize voice library
    try:
        voice_lib = get_voice_library()
        voices = voice_lib.list_voices()
        logger.info(f"✓ Voice library initialized with {len(voices)} voices")
    except Exception as e:
        logger.error(f"✗ Failed to initialize voice library: {e}")
        raise

    logger.info("=" * 60)
    logger.info(f"🚀 API ready at http://{settings.HOST}:{settings.PORT}")
    logger.info(f"📚 Docs at http://{settings.HOST}:{settings.PORT}{settings.API_PREFIX}/docs")
    logger.info("=" * 60)


# Health check endpoint
@app.get(f"{settings.API_PREFIX}/health", response_model=HealthResponse)
async def health_check():
    """
    Check API health status

    Returns service status, model information, and uptime
    """
    tts = get_tts_service()
    model_info = tts.get_model_info()

    return HealthResponse(
        status="healthy" if model_info["loaded"] else "unhealthy",
        version=settings.API_VERSION,
        model_loaded=model_info["loaded"],
        device=model_info["device"],
        uptime_seconds=time.time() - app_start_time
    )


# Main synthesis endpoint
@app.post(f"{settings.API_PREFIX}/speak", response_model=SpeakResponse)
async def synthesize_speech(
    request: SpeakRequest,
    background_tasks: BackgroundTasks
):
    """
    🎙️ **Convert text to speech with voice cloning**

    This is the main endpoint for AI phone agents. It converts text to
    natural-sounding speech using the specified voice.

    ## Parameters
    - **text**: Text to synthesize (1-5000 characters)
    - **voice_id**: Voice identifier from voice library
    - **context**: Conversation context (greeting, question, empathy, etc.)
    - **emotion**: Emotional tone (neutral, friendly, concerned, etc.)
    - **speed**: Speech speed multiplier (0.5-2.0)
    - **add_naturals**: Add natural speech patterns
    - **streaming**: Enable streaming response
    - **telephony_format**: Convert to 8kHz μ-law (phone format)

    ## Response
    Returns audio file with metadata including processing time and RTF

    ## Example
    ```json
    {
        "text": "Hi Sarah, calling about your appointment tomorrow.",
        "voice_id": "professional_female_01",
        "context": "greeting",
        "emotion": "friendly"
    }
    ```
    """
    metrics["total_requests"] += 1
    request_start = time.time()

    try:
        # Get voice library
        voice_lib = get_voice_library()

        # Validate voice exists
        voice_info = voice_lib.get_voice(request.voice_id)
        if not voice_info:
            raise HTTPException(
                status_code=404,
                detail=f"Voice '{request.voice_id}' not found. "
                       f"Use /voices endpoint to list available voices."
            )

        # Get voice sample path
        voice_sample_path = voice_lib.get_voice_sample_path(request.voice_id)
        if not voice_sample_path:
            raise HTTPException(
                status_code=500,
                detail=f"Voice sample file not found for '{request.voice_id}'"
            )

        # Get TTS service
        tts = get_tts_service()

        # Synthesize speech
        logger.info(
            f"Synthesizing for voice '{request.voice_id}': '{request.text[:50]}...'"
        )

        audio, processing_time = tts.synthesize(
            text=request.text,
            voice_sample_path=str(voice_sample_path),
            language=request.language,
            speed=request.speed
        )

        # Apply audio enhancements
        if request.add_naturals or request.telephony_format:
            audio = AudioProcessor.enhance_for_phone_calls(
                audio,
                sample_rate=settings.SAMPLE_RATE,
                text=request.text
            )

        # Convert to telephony format if requested
        sample_rate = settings.SAMPLE_RATE
        if request.telephony_format:
            audio, sample_rate = AudioProcessor.convert_to_telephony_format(
                audio,
                input_sample_rate=settings.SAMPLE_RATE
            )

        # Calculate metrics
        audio_duration = len(audio) / sample_rate
        rtf = processing_time / audio_duration

        # Update metrics
        metrics["total_audio_seconds"] += audio_duration
        metrics["total_processing_time"] += processing_time

        # Handle streaming response
        if request.streaming:
            # Stream audio in chunks
            def audio_stream():
                chunk_size = int(sample_rate * settings.CHUNK_SIZE_MS / 1000)
                for i in range(0, len(audio), chunk_size):
                    chunk = audio[i:i + chunk_size]
                    # Convert to bytes
                    buffer = io.BytesIO()
                    sf.write(buffer, chunk, sample_rate, format='WAV')
                    buffer.seek(0)
                    yield buffer.read()

            return StreamingResponse(
                audio_stream(),
                media_type="audio/wav",
                headers={
                    "X-Audio-Duration": str(audio_duration),
                    "X-Processing-Time": str(processing_time),
                    "X-RTF": str(rtf),
                    "X-Sample-Rate": str(sample_rate)
                }
            )

        # Non-streaming: save to file and return response
        output_filename = f"output_{uuid.uuid4().hex[:8]}.wav"
        output_path = settings.CACHE_DIR / output_filename

        # Save audio
        sf.write(output_path, audio, sample_rate)

        # Schedule cleanup
        background_tasks.add_task(cleanup_file, output_path)

        # Return response
        return SpeakResponse(
            audio_url=f"{settings.API_PREFIX}/audio/{output_filename}",
            duration=audio_duration,
            processing_time=processing_time,
            sample_rate=sample_rate,
            format="wav",
            real_time_factor=rtf
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Synthesis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")


# Serve generated audio files
@app.get(f"{settings.API_PREFIX}/audio/{{filename}}")
async def get_audio(filename: str):
    """
    Download generated audio file

    Audio files are automatically cleaned up after download
    """
    audio_path = settings.CACHE_DIR / filename

    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        audio_path,
        media_type="audio/wav",
        filename=filename
    )


# Voice library endpoints
@app.get(f"{settings.API_PREFIX}/voices", response_model=VoiceListResponse)
async def list_voices():
    """
    📚 **List all available voices**

    Returns list of all cloned voices in the library with metadata

    Use these voice IDs in the /speak endpoint
    """
    voice_lib = get_voice_library()
    voices = voice_lib.list_voices()

    return VoiceListResponse(
        voices=voices,
        total=len(voices)
    )


@app.get(f"{settings.API_PREFIX}/voices/{{voice_id}}", response_model=VoiceInfo)
async def get_voice(voice_id: str):
    """
    Get detailed information about a specific voice
    """
    voice_lib = get_voice_library()
    voice_info = voice_lib.get_voice(voice_id)

    if not voice_info:
        raise HTTPException(status_code=404, detail=f"Voice '{voice_id}' not found")

    return voice_info


@app.post(f"{settings.API_PREFIX}/voices", response_model=VoiceInfo, status_code=201)
async def create_voice(
    voice_data: VoiceCloneRequest,
    audio_file: UploadFile = File(...)
):
    """
    🎤 **Clone a new voice from audio sample**

    Upload 5-30 seconds of clear audio to create a new cloned voice

    ## Requirements
    - Audio duration: 5-30 seconds
    - Format: WAV, MP3, FLAC, M4A
    - Quality: Clear speech, minimal background noise
    - Single speaker

    ## Parameters
    - **voice_id**: Unique identifier (lowercase, alphanumeric, hyphens)
    - **name**: Human-readable name
    - **description**: Optional description
    - **tags**: Optional tags for categorization
    - **audio_file**: Audio sample file

    ## Returns
    Voice information including quality score
    """
    voice_lib = get_voice_library()

    # Check if voice already exists
    existing_voice = voice_lib.get_voice(voice_data.voice_id)
    if existing_voice:
        raise HTTPException(
            status_code=409,
            detail=f"Voice '{voice_data.voice_id}' already exists"
        )

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as tmp:
            content = await audio_file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        # Add voice to library
        voice_info = voice_lib.add_voice(
            voice_id=voice_data.voice_id,
            name=voice_data.name,
            audio_file_path=tmp_path,
            description=voice_data.description,
            tags=voice_data.tags
        )

        # Cleanup temp file
        tmp_path.unlink()

        logger.info(f"Created new voice: {voice_data.voice_id}")

        return voice_info

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create voice: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create voice: {str(e)}")


@app.delete(f"{settings.API_PREFIX}/voices/{{voice_id}}")
async def delete_voice(voice_id: str):
    """
    Delete a voice from the library
    """
    voice_lib = get_voice_library()

    success = voice_lib.delete_voice(voice_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Voice '{voice_id}' not found")

    return {"message": f"Voice '{voice_id}' deleted successfully"}


@app.get(f"{settings.API_PREFIX}/voices/{{voice_id}}/preview")
async def preview_voice(voice_id: str, text: str = "Hello, this is a preview of this voice."):
    """
    🔊 **Preview a voice**

    Generate a quick sample to hear what the voice sounds like

    ## Parameters
    - **voice_id**: Voice to preview
    - **text**: Text to synthesize (optional)
    """
    voice_lib = get_voice_library()

    # Validate voice
    voice_info = voice_lib.get_voice(voice_id)
    if not voice_info:
        raise HTTPException(status_code=404, detail=f"Voice '{voice_id}' not found")

    # Get voice sample path
    voice_sample_path = voice_lib.get_voice_sample_path(voice_id)

    # Synthesize preview
    tts = get_tts_service()
    audio, _ = tts.synthesize(
        text=text,
        voice_sample_path=str(voice_sample_path),
        language="en"
    )

    # Return as streaming audio
    buffer = io.BytesIO()
    sf.write(buffer, audio, settings.SAMPLE_RATE, format='WAV')
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="audio/wav")


@app.get(f"{settings.API_PREFIX}/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    📊 **Get API performance metrics**

    Returns statistics about API usage and performance
    """
    voice_lib = get_voice_library()
    voices = voice_lib.list_voices()

    avg_latency = (
        metrics["total_processing_time"] / metrics["total_requests"] * 1000
        if metrics["total_requests"] > 0
        else 0
    )

    avg_rtf = (
        metrics["total_processing_time"] / metrics["total_audio_seconds"]
        if metrics["total_audio_seconds"] > 0
        else 0
    )

    cache_total = metrics["cache_hits"] + metrics["cache_misses"]
    cache_hit_rate = (
        metrics["cache_hits"] / cache_total
        if cache_total > 0
        else 0
    )

    return MetricsResponse(
        total_requests=metrics["total_requests"],
        total_audio_generated_seconds=metrics["total_audio_seconds"],
        average_latency_ms=avg_latency,
        average_rtf=avg_rtf,
        cache_hit_rate=cache_hit_rate,
        active_voices=len(voices)
    )


# Utility functions
async def cleanup_file(file_path: Path, delay: int = 300):
    """Delete file after delay (default 5 minutes)"""
    import asyncio
    await asyncio.sleep(delay)
    try:
        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Cleaned up: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup {file_path}: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        workers=settings.WORKERS,
        log_level="info"
    )

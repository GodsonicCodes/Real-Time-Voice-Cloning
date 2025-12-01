"""
Modern TTS Service using Coqui XTTS v2
Provides fast, high-quality voice cloning for AI phone agents
"""
import torch
import torchaudio
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple
import time
import logging
from TTS.api import TTS

from api.config import settings

logger = logging.getLogger(__name__)


class VoiceCloningService:
    """
    Modern voice cloning service using XTTS v2
    - 10x faster than WaveRNN
    - Real-time capable (RTF < 0.5)
    - High quality, natural-sounding speech
    """

    def __init__(self):
        self.model: Optional[TTS] = None
        self.device = settings.TTS_DEVICE if torch.cuda.is_available() else "cpu"
        self._load_model()

    def _load_model(self):
        """Load XTTS v2 model"""
        logger.info(f"Loading XTTS v2 model on device: {self.device}")
        start_time = time.time()

        try:
            self.model = TTS(
                model_name=settings.TTS_MODEL_NAME,
                progress_bar=False,
                gpu=(self.device == "cuda")
            )

            # Move to appropriate device
            if self.device == "cuda":
                self.model.to(self.device)

            load_time = time.time() - start_time
            logger.info(f"✓ XTTS v2 model loaded in {load_time:.2f}s")

        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            raise

    def synthesize(
        self,
        text: str,
        voice_sample_path: str,
        language: str = "en",
        speed: float = 1.0,
        **kwargs
    ) -> Tuple[np.ndarray, float]:
        """
        Synthesize speech from text using voice cloning

        Args:
            text: Text to synthesize
            voice_sample_path: Path to reference voice audio
            language: Language code
            speed: Speech speed multiplier
            **kwargs: Additional synthesis parameters

        Returns:
            Tuple of (audio_array, processing_time)
        """
        if not self.model:
            raise RuntimeError("TTS model not loaded")

        logger.debug(f"Synthesizing: '{text[:50]}...' with voice: {voice_sample_path}")
        start_time = time.time()

        try:
            # Generate speech
            wav = self.model.tts(
                text=text,
                speaker_wav=voice_sample_path,
                language=language,
                speed=speed
            )

            # Convert to numpy array if needed
            if isinstance(wav, torch.Tensor):
                wav = wav.cpu().numpy()
            elif isinstance(wav, list):
                wav = np.array(wav)

            processing_time = time.time() - start_time
            audio_duration = len(wav) / settings.SAMPLE_RATE
            rtf = processing_time / audio_duration

            logger.info(
                f"Generated {audio_duration:.2f}s audio in {processing_time:.3f}s "
                f"(RTF: {rtf:.3f}x)"
            )

            return wav, processing_time

        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            raise

    def synthesize_streaming(
        self,
        text: str,
        voice_sample_path: str,
        language: str = "en",
        chunk_size_ms: int = 100,
        **kwargs
    ):
        """
        Generate speech with streaming support for lower latency

        Args:
            text: Text to synthesize
            voice_sample_path: Path to reference voice audio
            language: Language code
            chunk_size_ms: Size of audio chunks in milliseconds

        Yields:
            Audio chunks as numpy arrays
        """
        # For XTTS v2, we generate full audio then stream in chunks
        # A truly streaming implementation would require model modifications
        wav, _ = self.synthesize(text, voice_sample_path, language, **kwargs)

        # Calculate chunk size in samples
        chunk_size = int(settings.SAMPLE_RATE * chunk_size_ms / 1000)

        # Stream in chunks
        for i in range(0, len(wav), chunk_size):
            chunk = wav[i:i + chunk_size]
            yield chunk

    def get_model_info(self) -> dict:
        """Get information about loaded model"""
        return {
            "model_name": settings.TTS_MODEL_NAME,
            "device": self.device,
            "sample_rate": settings.SAMPLE_RATE,
            "loaded": self.model is not None,
            "supports_languages": [
                "en", "es", "fr", "de", "it", "pt", "pl",
                "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja"
            ]
        }


class AudioProcessor:
    """
    Audio post-processing for natural speech and telephony optimization
    """

    @staticmethod
    def add_natural_pauses(
        audio: np.ndarray,
        text: str,
        sample_rate: int = 24000
    ) -> np.ndarray:
        """
        Add natural micro-pauses at punctuation marks
        Makes AI speech sound more human
        """
        if not settings.ADD_NATURAL_PAUSES:
            return audio

        # Simple implementation: add brief silence at sentence boundaries
        # More sophisticated version would analyze text structure
        # For now, this is a placeholder that returns audio unchanged
        # Real implementation would segment audio and insert pauses

        return audio

    @staticmethod
    def add_breathing_sounds(
        audio: np.ndarray,
        sample_rate: int = 24000
    ) -> np.ndarray:
        """
        Add subtle breathing sounds between sentences
        Critical for human-like AI phone agents
        """
        if not settings.ADD_BREATHING:
            return audio

        # Placeholder - real implementation would:
        # 1. Detect silence regions
        # 2. Add subtle breath samples (low-pass filtered noise)
        # 3. Randomly place based on BREATH_PROBABILITY

        return audio

    @staticmethod
    def apply_telephony_filter(
        audio: np.ndarray,
        sample_rate: int = 24000
    ) -> np.ndarray:
        """
        Apply telephony bandpass filter (300Hz - 3.4kHz)
        Makes audio sound natural on phone calls
        """
        if not settings.APPLY_TELEPHONY_FILTER:
            return audio

        from scipy import signal

        # Design bandpass filter
        nyquist = sample_rate / 2
        low = settings.TELEPHONY_LOW_FREQ / nyquist
        high = settings.TELEPHONY_HIGH_FREQ / nyquist

        b, a = signal.butter(4, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, audio)

        return filtered

    @staticmethod
    def apply_compression(
        audio: np.ndarray,
        threshold_db: float = -20.0,
        ratio: float = 4.0
    ) -> np.ndarray:
        """
        Apply dynamic range compression for consistent volume
        Essential for phone calls
        """
        if not settings.APPLY_COMPRESSION:
            return audio

        # Simple compressor
        threshold_linear = 10 ** (threshold_db / 20)

        # Convert to dB
        audio_abs = np.abs(audio)
        audio_db = 20 * np.log10(audio_abs + 1e-8)

        # Apply compression
        compressed_db = np.where(
            audio_db > threshold_db,
            threshold_db + (audio_db - threshold_db) / ratio,
            audio_db
        )

        # Convert back to linear
        compressed = np.sign(audio) * (10 ** (compressed_db / 20))

        return compressed

    @staticmethod
    def convert_to_telephony_format(
        audio: np.ndarray,
        input_sample_rate: int = 24000
    ) -> Tuple[np.ndarray, int]:
        """
        Convert to 8kHz μ-law format (telephony standard)

        Args:
            audio: Input audio array
            input_sample_rate: Current sample rate

        Returns:
            Tuple of (resampled_audio, new_sample_rate)
        """
        import scipy.signal as signal

        # Resample to 8kHz
        target_rate = settings.TELEPHONY_SAMPLE_RATE
        num_samples = int(len(audio) * target_rate / input_sample_rate)
        resampled = signal.resample(audio, num_samples)

        # Apply telephony filter
        resampled = AudioProcessor.apply_telephony_filter(
            resampled,
            sample_rate=target_rate
        )

        # Apply compression
        resampled = AudioProcessor.apply_compression(resampled)

        # Normalize to int16 range for μ-law encoding
        resampled = np.clip(resampled, -1, 1)

        return resampled, target_rate

    @staticmethod
    def enhance_for_phone_calls(
        audio: np.ndarray,
        sample_rate: int = 24000,
        text: Optional[str] = None
    ) -> np.ndarray:
        """
        Full pipeline to make audio sound natural on phone calls

        Args:
            audio: Input audio
            sample_rate: Sample rate
            text: Original text (for pause detection)

        Returns:
            Enhanced audio array
        """
        # Apply all enhancements
        if text:
            audio = AudioProcessor.add_natural_pauses(audio, text, sample_rate)

        audio = AudioProcessor.add_breathing_sounds(audio, sample_rate)
        audio = AudioProcessor.apply_telephony_filter(audio, sample_rate)
        audio = AudioProcessor.apply_compression(audio)

        return audio


# Global singleton instance
_tts_service: Optional[VoiceCloningService] = None


def get_tts_service() -> VoiceCloningService:
    """Get or create TTS service singleton"""
    global _tts_service
    if _tts_service is None:
        _tts_service = VoiceCloningService()
    return _tts_service

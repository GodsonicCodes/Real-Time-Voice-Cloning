"""
Voice Library Management System
Handles voice cloning, storage, and retrieval
"""
import json
import shutil
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import logging
import hashlib
import librosa
import soundfile as sf
import numpy as np

from api.config import settings
from api.models import VoiceInfo

logger = logging.getLogger(__name__)


class VoiceLibrary:
    """
    Manages collection of cloned voices
    Stores voice samples and metadata
    """

    def __init__(self, voices_dir: Optional[Path] = None):
        self.voices_dir = voices_dir or settings.VOICES_DIR
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self._init_default_voices()

    def _init_default_voices(self):
        """Initialize with some default voice samples"""
        # Check if we have any voices
        existing_voices = self.list_voices()
        if existing_voices:
            logger.info(f"Found {len(existing_voices)} existing voices")
            return

        # Copy sample voices from the main repo
        sample_dir = Path("samples")
        if sample_dir.exists():
            logger.info("Initializing default voices from samples/")
            for sample_file in sample_dir.glob("*.mp3"):
                try:
                    voice_id = f"sample_{sample_file.stem}"
                    self.add_voice(
                        voice_id=voice_id,
                        name=f"Sample Voice {sample_file.stem}",
                        description="Default sample voice",
                        audio_file_path=sample_file,
                        tags=["sample", "default"]
                    )
                    logger.info(f"Added default voice: {voice_id}")
                except Exception as e:
                    logger.warning(f"Could not add sample {sample_file}: {e}")

    def add_voice(
        self,
        voice_id: str,
        name: str,
        audio_file_path: Path,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        language: str = "en"
    ) -> VoiceInfo:
        """
        Add a new voice to the library

        Args:
            voice_id: Unique identifier
            name: Human-readable name
            audio_file_path: Path to audio sample
            description: Optional description
            tags: Optional tags for categorization
            language: Language of the voice

        Returns:
            VoiceInfo object with voice details
        """
        voice_dir = self.voices_dir / voice_id
        voice_dir.mkdir(parents=True, exist_ok=True)

        # Validate and process audio
        audio, sr = librosa.load(str(audio_file_path), sr=settings.SAMPLE_RATE)
        duration = len(audio) / sr

        # Validate duration
        if duration < settings.MIN_SAMPLE_DURATION:
            raise ValueError(
                f"Audio too short ({duration:.1f}s). "
                f"Minimum: {settings.MIN_SAMPLE_DURATION}s"
            )

        if duration > settings.MAX_SAMPLE_DURATION:
            logger.warning(
                f"Audio longer than recommended ({duration:.1f}s). "
                f"Trimming to {settings.MAX_SAMPLE_DURATION}s"
            )
            audio = audio[:int(settings.MAX_SAMPLE_DURATION * sr)]
            duration = settings.MAX_SAMPLE_DURATION

        # Save processed audio
        sample_path = voice_dir / "sample.wav"
        sf.write(sample_path, audio, sr)

        # Create metadata
        metadata = {
            "voice_id": voice_id,
            "name": name,
            "description": description,
            "tags": tags or [],
            "language": language,
            "sample_count": 1,
            "total_duration": duration,
            "created_at": datetime.utcnow().isoformat(),
            "sample_rate": sr,
            "quality_score": self._calculate_quality_score(audio, sr)
        }

        # Save metadata
        metadata_path = voice_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Voice '{voice_id}' added successfully")

        return VoiceInfo(**metadata)

    def get_voice(self, voice_id: str) -> Optional[VoiceInfo]:
        """Get voice information by ID"""
        voice_dir = self.voices_dir / voice_id
        metadata_path = voice_dir / "metadata.json"

        if not metadata_path.exists():
            return None

        with open(metadata_path) as f:
            metadata = json.load(f)

        # Convert created_at string to datetime
        metadata["created_at"] = datetime.fromisoformat(metadata["created_at"])

        return VoiceInfo(**metadata)

    def get_voice_sample_path(self, voice_id: str) -> Optional[Path]:
        """Get path to voice sample audio file"""
        voice_dir = self.voices_dir / voice_id
        sample_path = voice_dir / "sample.wav"

        if not sample_path.exists():
            return None

        return sample_path

    def list_voices(self) -> List[VoiceInfo]:
        """List all available voices"""
        voices = []

        for voice_dir in self.voices_dir.iterdir():
            if voice_dir.is_dir():
                try:
                    voice_info = self.get_voice(voice_dir.name)
                    if voice_info:
                        voices.append(voice_info)
                except Exception as e:
                    logger.warning(f"Could not load voice {voice_dir.name}: {e}")

        return sorted(voices, key=lambda v: v.created_at, reverse=True)

    def delete_voice(self, voice_id: str) -> bool:
        """Delete a voice from the library"""
        voice_dir = self.voices_dir / voice_id

        if not voice_dir.exists():
            return False

        try:
            shutil.rmtree(voice_dir)
            logger.info(f"Voice '{voice_id}' deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to delete voice '{voice_id}': {e}")
            return False

    def update_voice_metadata(
        self,
        voice_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[VoiceInfo]:
        """Update voice metadata"""
        voice_info = self.get_voice(voice_id)
        if not voice_info:
            return None

        voice_dir = self.voices_dir / voice_id
        metadata_path = voice_dir / "metadata.json"

        with open(metadata_path) as f:
            metadata = json.load(f)

        # Update fields
        if name is not None:
            metadata["name"] = name
        if description is not None:
            metadata["description"] = description
        if tags is not None:
            metadata["tags"] = tags

        # Save updated metadata
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return self.get_voice(voice_id)

    def _calculate_quality_score(self, audio: np.ndarray, sr: int) -> float:
        """
        Calculate audio quality score (0-1)
        Based on SNR, clipping, and dynamic range
        """
        try:
            # Check for clipping
            clipping_ratio = np.sum(np.abs(audio) > 0.99) / len(audio)

            # Calculate signal-to-noise ratio (simplified)
            # Assume noise is in quiet regions
            sorted_audio = np.sort(np.abs(audio))
            noise_floor = np.mean(sorted_audio[:int(len(audio) * 0.1)])
            signal_level = np.mean(sorted_audio[int(len(audio) * 0.5):])
            snr = 20 * np.log10(signal_level / (noise_floor + 1e-10))

            # Calculate dynamic range
            dynamic_range = np.max(audio) - np.min(audio)

            # Combine metrics into quality score
            clipping_penalty = max(0, 1 - clipping_ratio * 10)
            snr_score = min(1.0, snr / 40.0)  # Normalize assuming 40dB is excellent
            dr_score = min(1.0, dynamic_range / 2.0)  # Normalize

            quality = (clipping_penalty * 0.3 + snr_score * 0.4 + dr_score * 0.3)

            return float(np.clip(quality, 0, 1))

        except Exception as e:
            logger.warning(f"Could not calculate quality score: {e}")
            return 0.5  # Default neutral score


# Global singleton
_voice_library: Optional[VoiceLibrary] = None


def get_voice_library() -> VoiceLibrary:
    """Get or create voice library singleton"""
    global _voice_library
    if _voice_library is None:
        _voice_library = VoiceLibrary()
    return _voice_library

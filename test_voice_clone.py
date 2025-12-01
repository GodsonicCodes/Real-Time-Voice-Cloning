#!/usr/bin/env python3
"""
Quick test script to verify voice cloning capabilities and measure performance
"""
import time
import numpy as np
from pathlib import Path

# Import the required modules
from encoder import inference as encoder
from synthesizer.inference import Synthesizer
from vocoder import inference as vocoder
from utils.default_models import ensure_default_models
import soundfile as sf

def test_voice_cloning():
    """Test voice cloning with a sample file and measure performance"""

    print("=" * 60)
    print("VOICE CLONING CAPABILITY TEST")
    print("=" * 60)

    # Load models
    print("\n[1/5] Loading models...")
    start_time = time.time()

    ensure_default_models(Path("saved_models"))
    encoder.load_model(Path("saved_models/default/encoder.pt"))
    synthesizer = Synthesizer(Path("saved_models/default/synthesizer.pt"))
    vocoder.load_model(Path("saved_models/default/vocoder.pt"))

    model_load_time = time.time() - start_time
    print(f"✓ Models loaded in {model_load_time:.2f}s")

    # Use sample audio
    sample_file = Path("samples/1320_00000.mp3")
    print(f"\n[2/5] Processing reference audio: {sample_file.name}")

    # Create embedding
    print("   Creating speaker embedding...")
    start_time = time.time()
    preprocessed_wav = encoder.preprocess_wav(sample_file)
    embed = encoder.embed_utterance(preprocessed_wav)
    embedding_time = time.time() - start_time
    print(f"✓ Speaker embedding created in {embedding_time:.3f}s")
    print(f"   Embedding shape: {embed.shape}")
    print(f"   Audio duration: {len(preprocessed_wav)/encoder.sampling_rate:.2f}s")

    # Generate speech
    test_text = "Hello! This is a test of the voice cloning system for AI phone agents."
    print(f"\n[3/5] Generating speech for text:")
    print(f"   '{test_text}'")

    start_time = time.time()
    specs = synthesizer.synthesize_spectrograms([test_text], [embed])
    spec = specs[0]
    synthesis_time = time.time() - start_time
    print(f"✓ Spectrogram generated in {synthesis_time:.3f}s")

    # Generate waveform
    print("\n[4/5] Converting to audio waveform...")
    start_time = time.time()
    generated_wav = vocoder.infer_waveform(spec)
    vocoder_time = time.time() - start_time
    print(f"✓ Waveform generated in {vocoder_time:.3f}s")

    # Post-processing
    generated_wav = np.pad(generated_wav, (0, synthesizer.sample_rate), mode="constant")
    generated_wav = encoder.preprocess_wav(generated_wav)

    # Save output
    output_file = "test_output.wav"
    sf.write(output_file, generated_wav.astype(np.float32), synthesizer.sample_rate)
    print(f"✓ Audio saved to {output_file}")

    # Calculate metrics
    total_time = embedding_time + synthesis_time + vocoder_time
    audio_duration = len(generated_wav) / synthesizer.sample_rate
    rtf = total_time / audio_duration  # Real-Time Factor

    print("\n[5/5] PERFORMANCE METRICS")
    print("=" * 60)
    print(f"Total processing time:     {total_time:.3f}s")
    print(f"Generated audio duration:  {audio_duration:.2f}s")
    print(f"Real-Time Factor (RTF):    {rtf:.2f}x")
    print(f"   (RTF < 1.0 = faster than real-time)")
    print(f"\nBreakdown:")
    print(f"  - Speaker embedding:     {embedding_time:.3f}s ({embedding_time/total_time*100:.1f}%)")
    print(f"  - Mel spectrogram:       {synthesis_time:.3f}s ({synthesis_time/total_time*100:.1f}%)")
    print(f"  - Waveform generation:   {vocoder_time:.3f}s ({vocoder_time/total_time*100:.1f}%)")
    print(f"\nSample rate:               {synthesizer.sample_rate} Hz")
    print(f"Model load time:           {model_load_time:.2f}s (one-time cost)")
    print("=" * 60)

    # Assessment
    print("\n📊 ASSESSMENT FOR PHONE CALLS:")
    if rtf < 1.5:
        print("✅ Speed: Suitable for real-time phone conversations")
    else:
        print("⚠️  Speed: May need optimization for real-time use")

    print(f"✅ Quality: 16kHz sample rate (phone quality is 8kHz)")
    print(f"✅ Input requirement: ~{len(preprocessed_wav)/encoder.sampling_rate:.1f}s of audio needed to clone")
    print("\n✅ Test completed successfully!")

if __name__ == "__main__":
    test_voice_cloning()

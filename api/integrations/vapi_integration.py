"""
Vapi.ai Integration Example
Webhook-based integration for custom voice in AI phone agents
"""
import asyncio
import httpx
from typing import Optional

# Vapi.ai Custom Voice Integration
# Documentation: https://docs.vapi.ai/


class VapiVoiceIntegration:
    """
    Integrate Voice Cloning API with Vapi.ai

    Vapi uses webhooks to request TTS from custom voice providers
    """

    def __init__(self, voice_api_url: str, voice_id: str):
        """
        Args:
            voice_api_url: Base URL of your voice cloning API
            voice_id: Voice ID to use from your library
        """
        self.voice_api_url = voice_api_url.rstrip('/')
        self.voice_id = voice_id

    async def synthesize_for_vapi(
        self,
        text: str,
        emotion: str = "friendly"
    ) -> bytes:
        """
        Synthesize speech for Vapi webhook

        Args:
            text: Text from Vapi
            emotion: Emotion/context from Vapi

        Returns:
            Audio bytes in telephony format
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.voice_api_url}/api/v1/speak",
                json={
                    "text": text,
                    "voice_id": self.voice_id,
                    "emotion": emotion,
                    "telephony_format": True,  # 8kHz μ-law for phone
                    "add_naturals": True,
                    "streaming": False
                }
            )

            if response.status_code != 200:
                raise Exception(f"API error: {response.text}")

            # Get audio URL from response
            data = response.json()
            audio_url = data["audio_url"]

            # Download audio
            audio_response = await client.get(
                f"{self.voice_api_url}{audio_url}"
            )

            return audio_response.content


# FastAPI webhook endpoint for Vapi
from fastapi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI()


@app.post("/vapi/tts")
async def vapi_tts_webhook(request: Request):
    """
    Webhook endpoint that Vapi calls for TTS

    Vapi sends:
    {
        "text": "Hello, how can I help you?",
        "emotion": "friendly",
        "voiceId": "your-voice-id"
    }

    Return raw audio bytes (WAV format)
    """
    data = await request.json()

    text = data.get("text", "")
    emotion = data.get("emotion", "neutral")
    voice_id = data.get("voiceId", "default_voice")

    # Call your voice API
    vapi_integration = VapiVoiceIntegration(
        voice_api_url="http://localhost:8000",
        voice_id=voice_id
    )

    audio_bytes = await vapi_integration.synthesize_for_vapi(text, emotion)

    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={
            "Content-Type": "audio/wav",
            "Content-Disposition": "inline"
        }
    )


# Configuration in Vapi Dashboard:
"""
1. Go to Vapi Dashboard -> Voice Settings
2. Select "Custom Voice Provider"
3. Enter webhook URL: https://your-domain.com/vapi/tts
4. Configure voice parameters
5. Test with a sample call

Example Vapi Assistant Configuration:
{
    "voice": {
        "provider": "custom",
        "webhookUrl": "https://your-domain.com/vapi/tts",
        "voiceId": "professional_female_01"
    },
    "model": {
        "provider": "openai",
        "model": "gpt-4"
    }
}
"""

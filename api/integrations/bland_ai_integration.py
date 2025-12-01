"""
Bland AI Integration Example
Custom voice integration for AI phone calls
"""
import httpx
import base64
from typing import Optional


class BlandAIVoiceIntegration:
    """
    Integrate Voice Cloning API with Bland AI

    Bland AI supports custom voices via webhook or audio URL
    """

    def __init__(self, voice_api_url: str, voice_id: str):
        """
        Args:
            voice_api_url: Base URL of your voice cloning API
            voice_id: Voice ID to use
        """
        self.voice_api_url = voice_api_url.rstrip('/')
        self.voice_id = voice_id

    async def create_bland_call(
        self,
        phone_number: str,
        task: str,
        bland_api_key: str,
        voice_id: Optional[str] = None
    ):
        """
        Create a phone call with Bland AI using custom voice

        Args:
            phone_number: Phone number to call
            task: Task/prompt for the AI agent
            bland_api_key: Your Bland AI API key
            voice_id: Override default voice ID
        """
        voice_id = voice_id or self.voice_id

        # Bland AI API call
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.bland.ai/v1/calls",
                headers={
                    "Authorization": f"Bearer {bland_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "phone_number": phone_number,
                    "task": task,
                    "voice": {
                        "provider": "custom",
                        "voice_id": voice_id,
                        "webhook_url": f"{self.voice_api_url}/bland/tts"
                    },
                    "voice_settings": {
                        "speed": 1.0,
                        "stability": 0.8
                    }
                }
            )

            return response.json()


# FastAPI webhook for Bland AI
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response

app = FastAPI()


@app.post("/bland/tts")
async def bland_tts_webhook(request: Request):
    """
    Webhook endpoint for Bland AI TTS requests

    Bland AI sends:
    {
        "text": "The text to synthesize",
        "voice_id": "your_voice_id",
        "context": "greeting|question|closing"
    }

    Return: Audio bytes (WAV or MP3)
    """
    try:
        data = await request.json()

        text = data.get("text")
        voice_id = data.get("voice_id", "default_voice")
        context = data.get("context", "neutral")

        if not text:
            raise HTTPException(status_code=400, detail="Text is required")

        # Call voice cloning API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/api/v1/speak",
                json={
                    "text": text,
                    "voice_id": voice_id,
                    "context": context,
                    "telephony_format": True,
                    "add_naturals": True,
                    "emotion": "friendly"
                }
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Voice API error: {response.text}"
                )

            # Get audio URL and download
            data = response.json()
            audio_url = data["audio_url"]

            audio_response = await client.get(
                f"http://localhost:8000{audio_url}"
            )

            return Response(
                content=audio_response.content,
                media_type="audio/wav"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Example usage:
"""
from bland_ai_integration import BlandAIVoiceIntegration

# Initialize integration
bland = BlandAIVoiceIntegration(
    voice_api_url="https://your-voice-api.com",
    voice_id="sales_agent_male"
)

# Make a call
await bland.create_bland_call(
    phone_number="+1234567890",
    task="You are a sales agent calling to schedule a product demo...",
    bland_api_key="your_bland_api_key"
)
"""

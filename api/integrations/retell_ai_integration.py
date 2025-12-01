"""
Retell AI Integration Example
WebSocket-based real-time voice streaming
"""
import asyncio
import json
import websockets
import httpx
from typing import AsyncIterator


class RetellAIVoiceIntegration:
    """
    Integrate Voice Cloning API with Retell AI

    Retell AI uses WebSocket for real-time bidirectional audio streaming
    """

    def __init__(self, voice_api_url: str, voice_id: str):
        self.voice_api_url = voice_api_url.rstrip('/')
        self.voice_id = voice_id

    async def synthesize_streaming(
        self,
        text: str
    ) -> AsyncIterator[bytes]:
        """
        Stream audio chunks for low-latency playback

        Args:
            text: Text to synthesize

        Yields:
            Audio chunks as bytes
        """
        async with httpx.AsyncClient() as client:
            # Request streaming response
            async with client.stream(
                "POST",
                f"{self.voice_api_url}/api/v1/speak",
                json={
                    "text": text,
                    "voice_id": self.voice_id,
                    "streaming": True,
                    "telephony_format": True,
                    "add_naturals": True
                }
            ) as response:
                async for chunk in response.aiter_bytes(chunk_size=4096):
                    yield chunk


# WebSocket server for Retell AI
import websockets
from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.websocket("/ws/retell")
async def retell_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for Retell AI integration

    Protocol:
    1. Retell sends: {"type": "text", "text": "Hello there", "voice_id": "..."}
    2. We stream back: Audio chunks
    3. Repeat for each utterance
    """
    await websocket.accept()

    try:
        while True:
            # Receive message from Retell AI
            data = await websocket.receive_json()

            if data.get("type") == "text":
                text = data.get("text")
                voice_id = data.get("voice_id", "default_voice")

                # Synthesize and stream audio
                integration = RetellAIVoiceIntegration(
                    voice_api_url="http://localhost:8000",
                    voice_id=voice_id
                )

                # Send audio chunks
                async for chunk in integration.synthesize_streaming(text):
                    await websocket.send_bytes(chunk)

                # Send end-of-utterance marker
                await websocket.send_json({"type": "audio_end"})

            elif data.get("type") == "close":
                break

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await websocket.close()


# Configuration for Retell AI:
"""
1. Deploy your WebSocket endpoint
2. In Retell AI Dashboard:
   - Go to Voice Settings
   - Select "Custom Voice Provider"
   - WebSocket URL: wss://your-domain.com/ws/retell
   - Enable streaming mode

3. Configure agent:
{
    "agent_name": "Customer Service Agent",
    "voice": {
        "provider": "custom",
        "websocket_url": "wss://your-domain.com/ws/retell",
        "voice_id": "professional_female_01"
    },
    "llm": {
        "provider": "openai",
        "model": "gpt-4"
    }
}
"""

# Example client test:
async def test_retell_websocket():
    """Test the WebSocket connection"""
    async with websockets.connect("ws://localhost:8000/ws/retell") as ws:
        # Send text
        await ws.send(json.dumps({
            "type": "text",
            "text": "Hello! How can I help you today?",
            "voice_id": "professional_female_01"
        }))

        # Receive audio chunks
        while True:
            message = await ws.recv()

            if isinstance(message, bytes):
                # Audio chunk received
                print(f"Received audio chunk: {len(message)} bytes")
            else:
                # JSON message
                data = json.loads(message)
                if data.get("type") == "audio_end":
                    print("Audio complete!")
                    break


if __name__ == "__main__":
    asyncio.run(test_retell_websocket())

from livekit.plugins import cartesia
from app.config import settings

def get_tts():
    """
    Returns the Cartesia TTS (Text-to-Speech) plugin.
    Cartesia provides ultra-low latency, natural sounding voices.
    """
    return cartesia.TTS(
        api_key=settings.CARTESIA_API_KEY,
        voice="f116e1cf-2277-48b8-8e4d-0ca051af9d46" # Default British male, can be configured
    )

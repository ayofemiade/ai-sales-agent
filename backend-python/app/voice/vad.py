from livekit.plugins import silero

def get_vad():
    """
    Returns the Silero VAD (Voice Activity Detection) plugin.
    Silero is efficient and works well for real-time voice applications.
    """
    return silero.VAD.load()

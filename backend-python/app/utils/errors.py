class AgentError(Exception):
    """Base class for agent exceptions"""
    pass

class LLMError(AgentError):
    """Raised when LLM service fails"""
    pass

class VoiceError(AgentError):
    """Raised when STT or TTS services fail"""
    pass

class SessionNotFoundError(AgentError):
    """Raised when a non-existent session is accessed"""
    pass

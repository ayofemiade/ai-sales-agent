from abc import ABC, abstractmethod
from typing import Optional

class BaseAgent(ABC):
    @abstractmethod
    async def generate_response(self, text: str, session_id: str) -> str:
        pass

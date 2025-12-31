from typing import List, Dict, Optional, Any
from collections import defaultdict
from app.agent.stages import SalesStage


class SessionMemory:
    def __init__(self):
        self._history: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        self._metadata: Dict[str, Dict[str, Any]] = defaultdict(dict)

        self._default_metadata = {
            "stage": SalesStage.GREETING,
            "mode": "SDR",
            "intent": None,
            "turns_in_stage": 0,
        }

    def _ensure_defaults(self, session_id: str):
        for key, value in self._default_metadata.items():
            self._metadata[session_id].setdefault(key, value)

    def add_message(self, session_id: str, role: str, content: str):
        self._history[session_id].append(
            {"role": role, "content": content}
        )
        if role == "user":
            self._ensure_defaults(session_id)
            self._metadata[session_id]["turns_in_stage"] += 1

    def get_history(self, session_id: str):
        return self._history[session_id]

    def clear_session(self, session_id: str):
        self._history.pop(session_id, None)
        self._metadata.pop(session_id, None)

    def set_metadata(self, session_id: str, key: str, value: Any):
        self._ensure_defaults(session_id)
        self._metadata[session_id][key] = value

    def get_metadata(self, session_id: str, key: str):
        self._ensure_defaults(session_id)
        return self._metadata[session_id].get(key, self._default_metadata.get(key))

    def advance_stage(self, session_id: str, next_stage: SalesStage):
        self.set_metadata(session_id, "stage", next_stage)
        self.set_metadata(session_id, "turns_in_stage", 0)

    def turns_in_stage(self, session_id: str) -> int:
        return self.get_metadata(session_id, "turns_in_stage")


session_memory = SessionMemory()

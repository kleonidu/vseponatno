
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class Step:
    prompt: str
    hint_levels: List[str] = field(default_factory=list)
    answer_checker: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TutorState:
    skill_id: str
    problem_text: str
    step_index: int = 0
    steps: List[Step] = field(default_factory=list)
    scratch: Dict[str, Any] = field(default_factory=dict)
    finished: bool = False

class MemoryStore:
    def __init__(self):
        self._data: Dict[int, TutorState] = {}

    def get(self, user_id: int) -> Optional[TutorState]:
        return self._data.get(user_id)

    def set(self, user_id: int, state: TutorState) -> None:
        self._data[user_id] = state

    def clear(self, user_id: int) -> None:
        self._data.pop(user_id, None)

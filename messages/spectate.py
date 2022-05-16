from dataclasses import asdict, dataclass
from typing import Optional

from messages.game_state import PlayerInfo

from .utils import dict_factory


@dataclass
class Spectate:
    player_index: Optional[int]
    player: Optional[PlayerInfo]

    def to_dict(self):
        return asdict(self, dict_factory=dict_factory)

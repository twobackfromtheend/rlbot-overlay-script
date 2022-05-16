from dataclasses import dataclass
from typing import Union


@dataclass
class Message:
    event: str
    data: Union[str, bytes, list, dict]

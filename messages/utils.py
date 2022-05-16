from typing import Any, List, Tuple


def dict_factory(data: List[Tuple[str, Any]]):
    """
    Rounds all floats to 2 decimal places
    """
    return {k: v if not isinstance(v, float) else round(v, 2) for k, v in data}

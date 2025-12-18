from syntree import Node

def resize_range(source_min: int, source_max: int, source: int, target_min: int, target_max: int) -> int:
    """
    returns `target: int`
    which is source but resized to the new range
    """

    source_percent = (source - source_min) / (source_max - source_min)
    target_value = target_min + source_percent * (target_max - target_min)
    return round(target_value)

def index_of(l: list[Node], o: Node) -> int:
    for i, e in enumerate(l):
        if o.nid == e.nid:
            return i

    raise ValueError()
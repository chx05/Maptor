from dataclasses import dataclass
from syntree import Node

@dataclass
class Editable:
    node: Node
    field_name: str
    x: float
    y: float

    def content(self) -> str:
        return getattr(self.node, self.field_name)

    def content_len(self) -> int:
        return len(self.content())
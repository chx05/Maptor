from typing import Any

class Node:
    def __init__(self, kind: str, child: 'Node | object') -> None:
        self.kind: str = kind
        self.child: Node | object = child
    
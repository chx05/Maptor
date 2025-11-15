from typing import Any

class Node:
    def __init__(self, nid: int) -> None:
        """
        nid => node id
        """
        self.nid: int = nid

class PDecl(Node):
    def __init__(self, name: str, value: Node):
        self.name: str = name
        self.value: Node = value


from dataclasses import dataclass


incremental_nid: int = -1

def next_nid() -> int:
    global incremental_nid

    incremental_nid += 1
    return incremental_nid


@dataclass
class Node:
    def __post_init__(self) -> None:
        # nid is node id
        # so the editor can have an internal associative
        # table to map nid -> canvas position of the node
        self.nid: int = next_nid()

@dataclass
class DeclNode:
    name: str
    value: Node

# --

@dataclass
class TypeNode(Node):
    pass

@dataclass
class PrimitiveTypeNode(TypeNode):
    kind: str

@dataclass
class StmtNode(Node):
    pass

@dataclass
class IncomeNode:
    name: str
    typing: TypeNode

@dataclass
class OutcomeNode:
    name: str
    typing: TypeNode

@dataclass
class FnNode(Node):
    ins: list[IncomeNode]
    outs: list[OutcomeNode]
    body: list[StmtNode]
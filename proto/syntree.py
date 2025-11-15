from dataclasses import dataclass


incremental_nid: int = -1

def next_nid() -> int:
    global incremental_nid

    incremental_nid += 1
    return incremental_nid


@dataclass
class PNode:
    def __post_init__(self) -> None:
        # nid is node id
        # so the editor can have an internal associative
        # table to map nid -> canvas position of the node
        self.nid: int = next_nid()

@dataclass
class PDecl:
    name: str
    value: PNode

# --

@dataclass
class NType(PNode):
    pass

@dataclass
class NPrimitiveType(NType):
    kind: str

@dataclass
class NStatement(PNode):
    pass

@dataclass
class NFunc(PNode):
    class Param:
        name: str
        ntype: NType

    params: list[Param]
    ret_ntype: NType
    body: list[NStatement]
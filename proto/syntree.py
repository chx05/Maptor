import string

from dataclasses import dataclass


PRIMITIVE_IDENTS = [
    "i32", "str", "chr"
]

IDENT_CHARS = string.digits + string.ascii_letters + "_"


incremental_nid: int = -1

def next_nid() -> int:
    global incremental_nid

    incremental_nid += 1
    return incremental_nid

class NodeBase:
    def __init__(self) -> None:
        # nid is node id
        # so the editor can have an internal associative
        # table to map nid -> canvas position of the node
        self.nid: int = next_nid()
        self.parent: Node | None = None
    
    def set_child(self, nid: int, new_value: "Node") -> None:
        for k, v in self.__dict__.items():
            if isinstance(v, Node) and v.nid == nid:
                self.__dict__[k] = new_value
                return

            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], Node):
                for i, e in enumerate(v):
                    if e.nid == nid:
                       v[i] = new_value
                       return

@dataclass
class Node(NodeBase):
    def __post_init__(self) -> None:
        super().__init__()

@dataclass
class DeclNode(Node):
    name: str
    value: Node
    doc: str = ""

    def __post_init__(self) -> None:
        self.value.parent = self
        super().__post_init__()

# --

@dataclass
class StmtNode(Node):
    pass

@dataclass
class ExprNode(Node):
    pass

@dataclass
class CallNode(StmtNode):
    callee: ExprNode
    ins: list[ExprNode]
    outs: list[str]

    def __post_init__(self) -> None:
        self.callee.parent = self
        for n in self.ins: n.parent = self
        super().__post_init__()

@dataclass
class IdentNode(ExprNode):
    name: str

@dataclass
class LitNode(ExprNode):
    value: object

@dataclass
class LitChrNode(LitNode):
    pass

@dataclass
class BinaryNode(ExprNode):
    l: ExprNode
    op: str
    r: ExprNode

    def __post_init__(self) -> None:
        self.l.parent = self
        self.r.parent = self
        super().__post_init__()

@dataclass
class IncomeNode(Node):
    name: str
    typing: ExprNode

    def __post_init__(self) -> None:
        self.typing.parent = self
        super().__post_init__()

@dataclass
class OutcomeNode(Node):
    name: str
    typing: ExprNode

    def __post_init__(self) -> None:
        self.typing.parent = self
        super().__post_init__()

@dataclass
class FnNode(Node):
    ins: list[IncomeNode]
    outs: list[OutcomeNode]
    body: list[StmtNode]

    def __post_init__(self) -> None:
        for n in self.ins: n.parent = self
        for n in self.outs: n.parent = self
        for n in self.body: n.parent = self
        super().__post_init__()

@dataclass
class AssignNode(StmtNode):
    assignee: ExprNode
    assigner: ExprNode

    def __post_init__(self) -> None:
        self.assignee.parent = self
        self.assigner.parent = self
        super().__post_init__()

@dataclass
class ReturnNode(StmtNode):
    pass

@dataclass
class IfNode(StmtNode):
    expr: ExprNode
    body: list[StmtNode]

    def __post_init__(self) -> None:
        self.expr.parent = self
        for n in self.body: n.parent = self
        super().__post_init__()

@dataclass
class ElseNode(StmtNode):
    ifnode: IfNode
    body: list[StmtNode]

    def __post_init__(self) -> None:
        self.ifnode.parent = self
        for n in self.body: n.parent = self
        super().__post_init__()

@dataclass
class PlaceholderNode(Node):
    value: str = ""

@dataclass
class StmtBufferNode(PlaceholderNode, StmtNode):
    pass

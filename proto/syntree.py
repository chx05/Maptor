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
class DeclNode(Node):
    name: str
    value: Node
    doc: str = ""

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

@dataclass
class IncomeNode(Node):
    name: str
    typing: ExprNode

@dataclass
class OutcomeNode(Node):
    name: str
    typing: ExprNode

@dataclass
class FnNode(Node):
    ins: list[IncomeNode]
    outs: list[OutcomeNode]
    body: list[StmtNode]

@dataclass
class AssignNode(StmtNode):
    assignee: ExprNode
    assigner: ExprNode

@dataclass
class ReturnNode(StmtNode):
    pass

@dataclass
class IfNode(StmtNode):
    expr: ExprNode
    body: list[StmtNode]

@dataclass
class ElseNode(StmtNode):
    ifnode: IfNode
    body: list[StmtNode]

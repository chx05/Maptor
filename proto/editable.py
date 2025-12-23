import string

from dataclasses import dataclass
from syntree import *

@dataclass
class SolidContent:
    length: int

@dataclass
class Editable:
    node: Node
    field_name: str | None
    x: float
    y: float

    # only available when field_name is None
    solid_content: None | SolidContent = None

    def is_quoted_lit(self) -> bool:
        return isinstance(self.node, (LitNode, LitChrNode)) and isinstance(self.node.value, str)

    def is_num_lit(self) -> bool:
        return isinstance(self.node, LitNode) and isinstance(self.node.value, int)
    
    def supports_char(self, c: str) -> bool:
        if c not in string.printable:
            return False
        
        match self.node:
            case IdentNode() | IncomeNode() | OutcomeNode() | DeclNode():
                return c in IDENT_CHARS
            case LitChrNode():
                return self.content_len() < 1
            case StmtBufferNode():
                return True
            case ExprBufferNode():
                return True
            case LitNode() if self.is_quoted_lit():
                return True
            case LitNode() if self.is_num_lit():
                return c.isdigit()
            case _:
                return False

    def content(self) -> str:
        if self.field_name == None:
            assert self.solid_content != None
            return " " * self.solid_content.length
        
        return str(getattr(self.node, self.field_name))
    
    def set_content(self, content: str):
        if self.field_name == None:
            assert self.solid_content != None
            self.solid_content.length = len(content)
        else:
            if self.is_num_lit():
                value = int(content)
            else:
                value = content
            
            setattr(self.node, self.field_name, value)

    def content_len(self) -> int:
        return len(self.content())

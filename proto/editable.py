from dataclasses import dataclass
from syntree import Node, LitNode, LitChrNode

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
        return isinstance(self.node, (LitNode, LitChrNode))

    def content(self) -> str:
        if self.field_name == None:
            assert self.solid_content != None
            return " " * self.solid_content.length
        
        return getattr(self.node, self.field_name)
    
    def set_content(self, content: str):
        if self.field_name == None:
            assert self.solid_content != None
            self.solid_content.length = len(content)
        else:
            setattr(self.node, self.field_name, content)

    def content_len(self) -> int:
        return len(self.content())

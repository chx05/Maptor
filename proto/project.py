from syntree import *

class Project:
    def __init__(self, res_path: str) -> None:
        t_i32 = PrimitiveTypeNode("i32")
        t_str = PrimitiveTypeNode("str")
        t_parsing_opts = PrimitiveTypeNode("ParsingOptions")
        t_node = PrimitiveTypeNode("Node")

        self.res_path: str = res_path
        self.decls: list[DeclNode] = [
            DeclNode(name="entry", value=FnNode(
                ins=[],
                outs=[],
                body=[]
            )),
            DeclNode(name="add", value=FnNode(
                ins=[
                    IncomeNode("a", t_i32),
                    IncomeNode("b", t_i32)
                ],
                outs=[OutcomeNode("r", t_i32)],
                body=[]
            )),
            DeclNode(name="parse", value=FnNode(
                ins=[
                    IncomeNode("expr", t_str),
                    IncomeNode("opts", t_parsing_opts)
                ],
                outs=[OutcomeNode("head", t_node), OutcomeNode("tail", t_node)],
                body=[]
            ))
        ]
    
    def load(self) -> None:
        # TODO: use json, read from res_path
        pass

    def save(self) -> None:
        # TODO: use json, save to res_path, overwrite
        pass

    def unload(self) -> None:
        # disposing data for the gc
        self.decls = []

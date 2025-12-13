from syntree import *

class Project:
    def __init__(self, res_path: str) -> None:
        t_i32 = IdentNode("i32")
        t_str = IdentNode("str")
        t_chr = IdentNode("chr")

        self.res_path: str = res_path
        self.decls: list[DeclNode] = [
            DeclNode(
                name="entry",
                doc="Entry point of the program,\njust like main.\nYes I'm writing random stuff\njust to showcase doc comments",
                value=FnNode(
                    ins=[],
                    outs=[],
                    body=[CallNode(IdentNode("print"), [LitNode("hello world!")], []), ReturnNode()]
                )
            ),
            DeclNode(name="add", value=FnNode(
                ins=[
                    IncomeNode("a", t_i32),
                    IncomeNode("b", t_i32)
                ],
                outs=[OutcomeNode("sum", t_i32)],
                body=[AssignNode(IdentNode("sum"), BinaryNode(IdentNode("a"), "+", IdentNode("b")))]
            )),
            DeclNode(name="split", value=FnNode(
                ins=[
                    IncomeNode("src", t_str),
                    IncomeNode("sep", t_chr)
                ],
                outs=[OutcomeNode("l", t_str), OutcomeNode("r", t_str)],
                body=[
                    IfNode(BinaryNode(IdentNode("src"), "=", LitNode(None)), body=[
                        CallNode(IdentNode("print"), [LitNode("Blocking: `src` param is null")], []),
                        ReturnNode()
                    ]),
                    IfNode(BinaryNode(IdentNode("sep"), "=", LitChrNode(' ')), body=[
                        CallNode(IdentNode("print"), [LitNode("Alert: `sep` param is space")], []),
                    ]),
                    CallNode(IdentNode("print"), [LitNode("All ok")], [])
                ]
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

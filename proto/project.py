from syntree import *

class Project:
    def __init__(self, res_path: str) -> None:
        self.res_path: str = res_path
        self.decls: list[PDecl] = [
            PDecl(name="entry", value=NFunc(
                params=[],
                ret_ntype=NPrimitiveType("int32"),
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

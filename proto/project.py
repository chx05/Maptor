from syntree import *

class Project:
    def __init__(self, res_path: str) -> None:
        self.res_path: str = res_path
        self.decls: list[PDecl] = []
    
    def load(self) -> None:
        # TODO: use json
        pass

    def unload(self) -> None:
        pass

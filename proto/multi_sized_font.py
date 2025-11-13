import pyray as pr

class AutoFont:
    def __init__(self, min_sz: int, max_sz: int, step: int = 10) -> None:
        # only multiples of 10
        assert min_sz % 10 == 0
        assert max_sz % 10 == 0

        self.min_sz: int = min_sz
        self.max_sz: int = max_sz
        self.step: int = step

        self.fonts: list[pr.Font] = []
        self.sizes = range(self.min_sz, self.max_sz + 1, self.step)
    
    def load(self, res_path: str) -> None:
        for sz in self.sizes:
            self.fonts.append(
                pr.load_font_ex(res_path, sz, None, 0)
            )
    
    def unload(self) -> None:
        for f in self.fonts:
            pr.unload_font(f)
    
    def get_best_font_from_size(self, sz: int) -> pr.Font:
        sz = 
        return self.
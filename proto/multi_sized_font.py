import pyray as pr

# TODO
# i should load font file data only once and then load the font data
# with different sizes from that same font file data i loaded

class MultiSizedFont:
    def __init__(self, min_sz: int, max_sz: int, step: int = 10) -> None:
        assert min_sz > 0

        assert min_sz % 5 == 0
        assert max_sz % 5 == 0
        assert step % 5 == 0

        self.min_sz: int = min_sz
        self.max_sz: int = max_sz
        self.step: int = step

        self.fonts: list[pr.Font] = []
        self.sizes: list[int] = list(range(self.min_sz, self.max_sz + 1, self.step))
        self.widths: list[float]

        assert len(self.sizes) >= 2

        self.cur_idx: int
    
    @property
    def cur_font(self) -> pr.Font:
        return self.fonts[self.cur_idx]

    def load(self, res_path: str) -> None:
        for sz in self.sizes:
            self.fonts.append(
                pr.load_font_ex(res_path, sz, None, 0)
            )
        
        self.widths = [pr.measure_text_ex(f, " ", sz, 0).x for sz, f in zip(self.sizes, self.fonts)]
    
    def unload(self) -> None:
        for f in self.fonts:
            pr.unload_font(f)
    
    def get_best_font_from_size(self, sz: int) -> int:
        """
        returns the font's index instead
        so i can use it to access the font's size as well
        """

        assert sz >= self.min_sz and sz <= self.max_sz

        font_idx = (sz - self.min_sz) // self.step
        return font_idx
    
    def refresh_most_suitable_font(self, sz: int) -> None:
        self.cur_idx = self.get_best_font_from_size(sz)
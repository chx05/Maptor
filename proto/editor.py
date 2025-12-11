import pyray as pr
import utils

from multi_sized_font import MultiSizedFont
from time import time
from project import Project
from syntree import *

class Editor:
    def __init__(self) -> None:
        self.bg = pr.Color(244, 245, 248, 255)
        self.fg = pr.Color(230, 109, 103, 255)
        self.txt = pr.Color(11, 10, 7, 255)
        self.text_wire = pr.color_alpha(self.txt, 0.3)
        self.nontext_wire = pr.color_alpha(self.text_wire, 0.15)
        self.dbg_gui_txt = pr.color_alpha(self.txt, 0.4)
        self.kw = pr.Color(232, 60, 145, 255)
        self.lit = pr.Color(98, 129, 65, 255)
        self.dot = pr.Color(0, 166, 251, 255)

        self.is_running: bool = True

        # msg + time of logging, in seconds
        self.logs: list[tuple[str, float]] = []

        self.gui_padding: int = 20
        self.interline_gap: float = 0.5
        self.interdecl_gap: float = 15
        self.indent_level_step: int = 2

        self.x: float
        self.y: float
        self.max_x: float
        self.base_x: float
        self.indent_level: int

    @property
    def w(self) -> int:
        return pr.get_screen_width()
    
    @property
    def h(self) -> int:
        return pr.get_screen_height()

    @property
    def screen_size(self) -> tuple[int, int]:
        return (self.w, self.h)
    
    @property
    def screen_center(self) -> tuple[float, float]:
        return (self.w / 2, self.h / 2)
    
    def refresh_running_state(self) -> None:
        ctrl = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL)

        if pr.is_key_pressed(pr.KeyboardKey.KEY_M):
            pr.minimize_window()

        if pr.window_should_close():
            self.is_running = False
        
        q = pr.is_key_pressed(pr.KeyboardKey.KEY_Q)
        if ctrl and q:
            self.is_running = False

    def launch(self) -> None:
        pr.init_window(0, 0, "Maptor [proto | beta]")
        pr.toggle_fullscreen()
        pr.set_target_fps(pr.get_monitor_refresh_rate(pr.get_current_monitor()))
        
        self.load_stuff()
        
        while self.is_running:
            self.inputs()

            pr.begin_drawing()
            pr.clear_background(self.bg)

            pr.begin_mode_2d(self.cam)
            self.canvas()
            pr.end_mode_2d()
            
            self.gui()
            pr.end_drawing()

            self.refresh_running_state()
        
        self.unload_stuff()
        pr.close_window()

    def canvas(self) -> None:
        self.x = 0
        self.y = 0
        self.max_x = 0
        self.base_x = 0
        self.indent_level = 0

        for decl in self.prj.decls:
            if not self.is_decl_visible(decl):
                continue

            self.decl(decl)
            # flushing last line
            self.flat_carry()

            self.indent_level = 0
            self.base_x = self.max_x + self.adjust(self.interdecl_gap)
            self.x = self.base_x
            self.y = 0
        
    def is_decl_visible(self, decl: DeclNode) -> bool:
        # TODO: render only visible nodes
        return True
    
    def decl(self, decl: DeclNode) -> None:
        self.text(decl.name, self.txt)
        
        match decl.value:
            case FnNode():
                self.fn_node(decl.value)

            case _:
                raise NotImplementedError(decl.value.__class__)

    def adjust(self, length: float) -> float:
        return self.font_h_to_w_ratio * self.text_size * length
    
    def hadjust(self, height: float) -> float:
        return self.text_size * height
    
    def gap(self, length: float) -> None:
        self.x += self.adjust(length)

    def fn_node_head(self, fn: FnNode) -> None:
        self.gap(0.25)
        self.wire("(")

        if len(fn.ins) + len(fn.outs) == 0:
            self.wire(")")
            self.flat_carry()
            self.flat_carry()
            return

        self.indent()
        self.icarry()
        
        for p in fn.ins:
            self.text(p.name, self.txt)
            self.typing_note_wire()
            self.typing(p.typing)

            self.icarry()
        
        for o in fn.outs:
            self.text("out", self.kw)
            self.one()
            self.text(o.name, self.txt)
            self.typing_note_wire()
            self.typing(o.typing)

            self.icarry()

        self.x -= self.adjust(self.indent_level)
        self.wire(")")

        self.unindent()
        self.flat_carry()
        self.flat_carry()

    def fn_node(self, fn: FnNode) -> None:
        self.fn_node_head(fn)

        self.vborderwire(self.y + self.hadjust(self.interline_gap) * 2 - self.hadjust(self.interline_gap) + self.hadjust(2))
        self.one()
        self.one()
        self.text("print", self.txt)
        self.gap(0.25)
        self.wire("(")
        self.text('"Hello World!"', self.lit)
        self.wire(")")
        self.icarry()
        self.one()
        self.one()
        self.text("return", self.kw)
        self.one()
        self.text("10", self.lit)
    
    def one(self, n: int = 1) -> None:
        self.text(" " * n, self.txt)

    def update_xmax(self, max_x: float) -> float:
        if self.x > max_x:
            return self.x
        
        return max_x

    def typing_note_wire(self) -> None:
        self.text(": ", self.text_wire)

    def typing(self, t: TypeNode) -> None:
        match t:
            case PrimitiveTypeNode():
                self.text(t.kind, self.fg)
            
            case _:
                raise NotImplementedError(t.__class__)
    
    def hborderwire(self, end_x: float) -> None:
        self.flat_carry()
        pr.draw_line_ex((self.x, self.y), (end_x, self.y), self.adjust(0.2), self.nontext_wire)
        self.flat_carry()
    
    def vborderwire(self, end_y: float) -> None:
        x_padding = self.adjust(0.5)
        pr.draw_line_ex((x_padding + self.x, self.y), (x_padding + self.x, end_y), self.adjust(0.2), self.nontext_wire)

    def wire(self, txt: str) -> None:
        self.text(txt, self.text_wire)

    def is_mouse_over_box(self, pos: pr.Vector2, side_size: float) -> bool:
        m = pr.get_screen_to_world_2d(pr.get_mouse_position(), self.cam)
        self.log(f"m: {m.x},{m.y} | pos: {pos.x},{pos.y}")
        return (
            m.x >= pos.x and m.x <= pos.x + side_size
            and
            m.y >= pos.y and m.y <= pos.y + side_size
        )
    
    def flat_carry(self) -> None:
        if self.x > self.max_x:
            self.max_x = self.x
        
        self.x = self.base_x
        self.y += self.text_size + self.hadjust(self.interline_gap)
    
    def icarry(self) -> None:
        self.flat_carry()
        self.x += self.adjust(self.indent_level)
    
    def carry_at(self, desired_x: float) -> None:
        self.flat_carry()
        self.x = desired_x
    
    def indent(self) -> None:
        self.indent_level += self.indent_level_step

    def unindent(self) -> None:
        self.indent_level -= self.indent_level_step
    
    def text(self, text: str, color: pr.Color) -> None:
        pr.draw_text_ex(
            self.code_font.cur_font,
            text,
            (self.x, self.y),
            self.text_size,
            1,
            color
        )

        m = pr.measure_text_ex(
            self.code_font.cur_font, text, self.text_size, 1
        )

        self.x += m.x

    def gui(self) -> None:
        self.display_fps()
        self.display_logs()
    
    def display_fps(self) -> None:
        fps_text = str(pr.get_fps())
        pr.draw_text_ex(
            self.gui_font,
            fps_text,
            (self.gui_padding, self.gui_padding),
            self.gui_font_size,
            1,
            self.dbg_gui_txt
        )
    
    def display_logs(self) -> None:
        for i, (msg, _) in enumerate(reversed(self.logs)):
            measure = pr.measure_text_ex(self.gui_font, msg, self.gui_font_size, 1)

            pr.draw_text_ex(
                self.gui_font,
                msg,
                (
                    self.w - measure.x - self.gui_padding,
                    self.gui_padding + (measure.y + self.gui_padding) * i
                ),
                self.gui_font_size,
                1,
                pr.color_alpha(
                    self.dbg_gui_txt,
                    1 - i / len(self.logs)
                )
            )

        # i remove all the old messages (they expire after N seconds)
        expiration_time = 5
        t = time()
        self.logs = list(filter(lambda l: t < l[1] + expiration_time, self.logs))

    def log(self, msg: str) -> None:
        max_capacity = 10
        if len(self.logs) >= max_capacity:
            self.logs.pop(0)

        self.logs.append((msg, time()))

    def inputs(self) -> None:
        ctrl = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL)

        shift = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_SHIFT)
        mouse_dx_btn = pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_RIGHT)
        if mouse_dx_btn or shift:
            delta = pr.get_mouse_delta()
            delta = pr.vector2_scale(delta, -1 / self.cam.zoom)
            self.cam.target = pr.vector2_add(self.cam.target, delta)
        
        mouse_scroll = pr.get_mouse_wheel_move()

        KEY_PLUS = 93
        if mouse_scroll > 0 or (ctrl and pr.is_key_pressed(KEY_PLUS)):
            mouse_scroll = +self.code_font.step

        KEY_MINUS = 47
        if mouse_scroll < 0 or (ctrl and pr.is_key_pressed(KEY_MINUS)):
            mouse_scroll = -self.code_font.step

        if mouse_scroll != 0:
            self.text_size += mouse_scroll
            self.cap_text_size()
            self.refresh_code_font()
    
    def cap_text_size(self) -> None:
        val = self.text_size
        minsz = self.code_font.min_sz
        maxsz = self.code_font.max_sz

        if val < minsz:
            val = minsz
        
        if val > maxsz:
            val = maxsz
        
        self.text_size = val

    def refresh_code_font(self) -> None:
        self.code_font.refresh_most_suitable_font(int(self.text_size))

    def load_stuff(self) -> None:
        self.cam: pr.Camera2D = pr.Camera2D(
            self.screen_center,
            (0, 0),
            0,
            1
        )

        self.code_font: MultiSizedFont = MultiSizedFont(10, 50, step=5)
        #self.code_font.load("res/3270.ttf")
        self.code_font.load("res/hurmit.otf")
        #self.code_font.load("res/agave.ttf")
        #self.code_font.load("res/jetbrains.ttf")
        self.text_size: float = 30
        self.refresh_code_font()

        self.gui_font_size: int = 20
        self.gui_font: pr.Font = self.code_font.fonts[self.code_font.get_best_font_from_size(self.gui_font_size)]

        m = pr.measure_text_ex(self.code_font.cur_font, " ", self.text_size, 1)
        self.font_h_to_w_ratio = m.x / m.y

        self.prj: Project = Project("res/my_project.mpt")
        self.prj.load()
    
    def unload_stuff(self) -> None:
        self.code_font.unload()
        self.prj.unload()
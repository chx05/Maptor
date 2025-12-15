import pyray as pr
import utils
import string

from multi_sized_font import MultiSizedFont
from time import time
from project import Project
from syntree import *
from editable import *

PRIMITIVE_IDENTS = [
    "i32", "str"
]

class Editor:
    def __init__(self) -> None:
        self.bg = pr.Color(244, 245, 248, 255)
        self.tc_typing = pr.Color(241, 162, 8, 255)
        self.tc_normal = pr.Color(11, 10, 7, 255)
        self.tc_wire = pr.color_alpha(self.tc_normal, 0.3)
        self.tc_shapewire = pr.color_alpha(self.tc_wire, 0.15)
        self.tc_dbg_gui = pr.color_alpha(self.tc_normal, 0.4)
        self.tc_kw = pr.Color(216, 49, 91, 255)
        self.tc_lit = pr.Color(6, 167, 125, 255)
        self.tc_fn_name = pr.Color(130, 106, 237, 255)

        self.is_running: bool = True
        self.parallel_view_mode: bool = False
        self.editables: dict[int, Editable] = {}

        self.logs: dict[str, str] = {}

        self.gui_padding: int = 20
        self.interline_gap: float = 0.25
        self.interdecl_gap: float = 25
        self.indent_level_step: float = 0.5
        self.fn_call_par_gap: float = 0.25
        self.stmt_side_padding: float = 2
        self.codewire_left_padding: float = 0.5
        self.shapewire_thick: float = 0.2

        self.x: float
        self.y: float
        self.max_x: float
        self.base_x: float
        self.indent_level: float

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

            pr.begin_drawing()
            pr.clear_background(self.bg)

            pr.begin_mode_2d(self.cam)
            self.canvas()
            self.handle_editables()
            self.inputs()
            pr.end_mode_2d()
            
            self.gui()
            pr.end_drawing()

            self.refresh_running_state()
        
        self.unload_stuff()
        pr.close_window()

    def handle_editables(self) -> None:
        mouse_pos = pr.get_screen_to_world_2d(pr.get_mouse_position(), self.cam)
        
        for e in self.editables.values():
            bounding_box = pr.Rectangle(
                e.x, e.y,
                self.adjust(e.content_len() * 1.1),
                self.text_size)
            
            hover = pr.check_collision_point_rec(mouse_pos, bounding_box)
            if hover:
                pr.draw_rectangle_rec(bounding_box, self.tc_shapewire)

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
        if decl.doc != "":
            self.doc(decl.doc)
            self.flat_carry()
        
        self.editable(decl, "name", self.tc_fn_name)
        
        match decl.value:
            case FnNode():
                self.fn_node(decl.value)

            case _:
                raise NotImplementedError(decl.value.__class__)

    def doc(self, s: str) -> None:
        lines = s.split("\n")
        height = self.vadjust(1) * len(lines) + self.vadjust(self.interline_gap) * (len(lines)-1)
        self.y -= height
        self.codewire(self.y + height)
        
        self.stmt_left_pad()
        
        for i, l in enumerate(lines):
            is_last_line = i != len(lines) - 1

            pieces = l.split("`")
            for j, p in enumerate(pieces):
                is_highlighted_piece = j % 2 == 1
                if is_highlighted_piece:
                    self.text(p, pr.color_alpha(self.tc_wire, 0.65))
                else:
                    self.text(p, self.tc_wire)

            if is_last_line:
                self.flat_carry()
        
        self.stmt_left_unpad()

    def adjust(self, length: float) -> float:
        return self.font_h_to_w_ratio * self.vadjust(length)
    
    def vadjust(self, height: float) -> float:
        return self.text_size * height
    
    def gap(self, length: float) -> None:
        self.x += self.adjust(length)

    def fn_node_head(self, fn: FnNode) -> None:
        self.gap(self.fn_call_par_gap)
        self.wire("(")

        if len(fn.ins) + len(fn.outs) == 0:
            self.wire(")")
            self.flat_carry()
            self.flat_carry()
            return

        param_left_padding = 2
        self.indent(param_left_padding)
        self.icarry()
        
        for p in fn.ins:
            self.editable(p, "name", self.tc_normal)
            self.typing_note_wire()
            self.expr(p.typing)

            self.icarry()
        
        for o in fn.outs:
            self.text("out", self.tc_kw)
            self.one()
            self.editable(o, "name", self.tc_normal)
            self.typing_note_wire()
            self.expr(o.typing)

            self.icarry()

        self.unindent(param_left_padding)
        self.wire(")")

        self.flat_carry()
        self.flat_carry()

    def fn_node(self, fn: FnNode) -> None:
        self.fn_node_head(fn)
        self.body(fn.body)
    
    def body(self, sts: list[StmtNode]) -> None:
        if len(sts) == 0:
            return

        for i, s in enumerate(sts):
            is_last = i == len(sts) - 1
            self.codewire_auto(s, is_last)
            
            self.stmt_left_pad()
            self.stmt(s)
            self.stmt_left_unpad()
            self.icarry()

    def codewire_auto(self, s: StmtNode, is_last: bool) -> None:
        if is_last or hasattr(s, "body"):
            self.codewire_flowstop(1)
        else:
            self.codewire(self.y + self.vadjust(1 + self.interline_gap))

    def codewire_flowstop(self, wire_len) -> None:
        y_end = self.y + self.vadjust(wire_len)/2
        self.codewire(y_end)
        left_padding = self.adjust(self.codewire_left_padding)
        pr.draw_line_ex(
            (left_padding + self.x, y_end),
            (left_padding + self.x + self.adjust(0.75), y_end),
            self.adjust(self.shapewire_thick),
            self.tc_shapewire)

    def stmt_left_pad(self):
        self.indent(self.stmt_side_padding)
        
    def stmt_left_unpad(self) -> None:
        self.unindent(self.stmt_side_padding)

    def stmt(self, s: StmtNode) -> None:
        match s:
            case ReturnNode():
                self.text("return", self.tc_kw)
            
            case CallNode():
                assert isinstance(s.callee, IdentNode)
                assert len(s.ins) <= 1
                assert len(s.outs) == 0

                self.editable(s.callee, "name", self.tc_fn_name)
                self.gap(self.fn_call_par_gap)
                self.wire("(")
                if len(s.ins) > 0:
                    self.expr(s.ins[0])
                self.wire(")")
            
            case IfNode():
                self.text("if", self.tc_kw)
                self.one()
                self.expr(s.expr)
                self.scope_indent()
                self.icarry()
                self.body(s.body)
                self.scope_unindent()
            
            case ElseNode():
                if self.parallel_view_mode:
                    old = self.max_x
                    self.max_x = self.x
                    old_y = self.y
                    self.stmt(s.ifnode)
                    self.flat_carry()
                    old_base_x = self.base_x
                    self.base_x = self.max_x + self.adjust(5)
                    self.x = self.base_x
                    self.y = old_y
                    self.max_x = old
                    self.text("else", self.tc_kw)
                    self.scope_indent()
                    self.icarry()
                    self.body(s.body)
                    self.scope_unindent()
                    self.base_x = old_base_x
                else:
                    self.stmt(s.ifnode)
                    self.text("else", self.tc_kw)
                    self.scope_indent()
                    self.icarry()
                    self.body(s.body)
                    self.scope_unindent()
            
            case AssignNode():
                self.expr(s.assignee)
                self.one()
                self.text("=", self.tc_kw)
                self.one()
                self.expr(s.assigner)

            case _:
                raise NotImplementedError(s.__class__)

    def expr(self, e: ExprNode) -> None:
        match e:
            case IdentNode():
                starts_with_capital = e.name[0] in string.ascii_uppercase
                if starts_with_capital or e.name in PRIMITIVE_IDENTS:
                    self.editable(e, 'name', self.tc_typing)
                else:
                    self.editable(e, 'name', self.tc_normal)
            
            case LitChrNode():
                assert isinstance(e.value, str)
                self.text("'" + repr('"' + e.value).removeprefix("'\""), self.tc_lit)

            case LitNode():
                match e.value:
                    case None:
                        self.text("null", self.tc_lit)
                    case bool():
                        self.text("true" if e.value else "false", self.tc_lit)
                    case str():
                        self.text('"' + repr("'" + e.value).removeprefix('"\''), self.tc_lit)
                    case _:
                        self.text(repr(e.value), self.tc_lit)
            
            case BinaryNode():
                # TODO add parenthesis when exprs must have implicit precedence
                # or maybe just add EnclosedNode
                self.expr(e.l)
                self.one()
                self.text(e.op, self.tc_kw)
                self.one()
                self.expr(e.r)

            case _:
                raise NotImplementedError(e.__class__)

    def one(self, n: int = 1) -> None:
        self.text(" " * n, self.tc_normal)

    def update_xmax(self, max_x: float) -> float:
        if self.x > max_x:
            return self.x
        
        return max_x

    def typing_note_wire(self) -> None:
        self.text(": ", self.tc_wire)
    
    def borderwire(self, end_x: float) -> None:
        self.flat_carry()
        pr.draw_line_ex((self.x, self.y), (end_x, self.y), self.adjust(self.shapewire_thick), self.tc_shapewire)
        self.flat_carry()
    
    def codewire(self, end_y: float) -> None:
        left_padding = self.adjust(self.codewire_left_padding)
        pr.draw_line_ex((left_padding + self.x, self.y), (left_padding + self.x, end_y), self.adjust(self.shapewire_thick), self.tc_shapewire)

    def wire(self, txt: str) -> None:
        self.text(txt, self.tc_wire)

    def flat_carry(self) -> None:
        if self.x > self.max_x:
            self.max_x = self.x
        
        self.x = self.base_x
        self.y += self.text_size + self.vadjust(self.interline_gap)
    
    def icarry(self) -> None:
        self.flat_carry()
        self.x += self.adjust(self.indent_level)
    
    def carry_at(self, desired_x: float) -> None:
        self.flat_carry()
        self.x = desired_x
    
    def indent(self, length: float, sign: int = +1) -> None:
        self.base_x += sign*self.adjust(length)
        self.x += sign*self.adjust(length)

    def unindent(self, length: float) -> None:
        self.indent(length, -1)
    
    def scope_indent(self) -> None:
        self.indent(self.indent_level_step)

    def scope_unindent(self) -> None:
        self.unindent(self.indent_level_step)
    
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
    
    def editable(self, node: Node, field_name: str, color: pr.Color) -> None:
        start_x = self.x
        start_y = self.y
        self.text(getattr(node, field_name), color)
        self.editables[node.nid] = Editable(node, field_name, start_x, start_y)

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
            self.tc_dbg_gui
        )
    
    def display_logs(self) -> None:
        for i, (tag, msg) in enumerate(self.logs.items()):
            content = f"{tag}: {msg}"
            measure = pr.measure_text_ex(self.gui_font, content, self.gui_font_size, 1)

            pr.draw_text_ex(
                self.gui_font,
                content,
                (
                    self.w - measure.x - self.gui_padding,
                    self.gui_padding + (measure.y + self.gui_padding) * i
                ),
                self.gui_font_size,
                1,
                self.tc_dbg_gui
            )

    def log(self, tag: str, msg: str) -> None:
        self.logs[tag] = msg

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
            world_mouse_x = self.cam.target.x
            world_mouse_y = self.cam.target.y

            anchor_x = world_mouse_x / self.text_size
            anchor_y = world_mouse_y / self.text_size

            self.text_size += mouse_scroll
            self.cap_text_size()
            self.refresh_code_font()

            # moving camera to anchor point (center of viewport)
            new_world_mouse_x = anchor_x * self.text_size
            new_world_mouse_y = anchor_y * self.text_size
            self.cam.target.x = new_world_mouse_x
            self.cam.target.y = new_world_mouse_y

        
        if ctrl and pr.is_key_pressed(pr.KeyboardKey.KEY_P):
            self.parallel_view_mode = not self.parallel_view_mode
    
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
        self.text_size: float = 20
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
"""pf3: read-only folder tree for the terminal."""
import sys
from pathlib import Path

from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.scrollbar import ScrollBar, ScrollBarRender
from textual.widgets import DirectoryTree, Footer
from rich.segment import Segment, Segments
from rich.style import Style
from watchfiles import awatch

try:
    from icons_data import EXTENSION_ICONS, FILENAME_ICONS
except ImportError:
    from .icons_data import EXTENSION_ICONS, FILENAME_ICONS


def _i(code: int) -> str:
    return chr(code)


FOLDER_CLOSED = _i(0xF0256)  # outline
FOLDER_OPEN = _i(0xF024B)  # filled
FILE_DEFAULT = (_i(0xF0224), "default")

# Glyphs that looked odd in kitty, replaced by hand.
OVERRIDES = {"md": (0xF00BA, "cyan"), "markdown": (0xF00BA, "cyan")}


def file_icon(name: str) -> tuple[str, str]:
    low = name.lower()
    hit = FILENAME_ICONS.get(name) or FILENAME_ICONS.get(low)
    if hit is None or hit[0] == 0xF00BA:
        hit = OVERRIDES.get(low.rsplit(".", 1)[-1], hit)
    if hit is None:
        ext = low.rsplit(".", 1)[-1] if "." in low else ""
        hit = EXTENSION_ICONS.get(name.rsplit(".", 1)[-1]) or EXTENSION_ICONS.get(ext)
    if hit is None:
        return FILE_DEFAULT
    return _i(hit[0]), hit[1] or "default"


class ThinScrollBarRender(ScrollBarRender):
    """Thin scrollbar: half-width thumb (vertical) or thin line (horizontal)."""

    THUMB_V = "\u2590"  # right half block
    THUMB_H = "\u2582"  # lower quarter block

    @classmethod
    def render_bar(cls, size=25, virtual_size=50, window_size=20, position=0,
                   thickness=1, vertical=True, back_color=None, bar_color=None):
        size = int(size)
        track_up = Style(bgcolor=back_color, meta={"@mouse.down": "scroll_up"})
        track_down = Style(bgcolor=back_color, meta={"@mouse.down": "scroll_down"})
        thumb_style = Style(color=bar_color, bgcolor=back_color,
                            meta={"@mouse.down": "grab"})
        width = thickness if vertical else 1
        blank = " " * width
        glyph = (cls.THUMB_V if vertical else cls.THUMB_H) * width
        if window_size and size and virtual_size and size != virtual_size:
            thumb = max(1, round(window_size / (virtual_size / size)))
            span = virtual_size - window_size
            start = round((size - thumb) * (position / span)) if span else 0
            start = max(0, min(start, size - thumb))
            end = start + thumb
            segments = (
                [Segment(blank, track_up)] * start
                + [Segment(glyph, thumb_style)] * thumb
                + [Segment(blank, track_down)] * (size - end)
            )
        else:
            segments = [Segment(blank, Style(bgcolor=back_color))] * size
        if vertical:
            return Segments(segments, new_lines=True)
        return Segments((segments + [Segment.line()]) * thickness, new_lines=False)


ScrollBar.renderer = ThinScrollBarRender


class PathTree(DirectoryTree):
    BINDINGS = [
        Binding("j", "cursor_down", "Descer", show=False),
        Binding("k", "cursor_up", "Subir", show=False),
        Binding("l,right", "expand", "Abrir", show=False),
        Binding("h,left", "collapse", "Fechar", show=False),
        Binding("L,shift+right", "pan(8)", "Direita", show=False),
        Binding("H,shift+left", "pan(-8)", "Esquerda", show=False),
        Binding("g,home", "scroll_home", "Topo", show=False),
        Binding("G,end", "scroll_end", "Fim", show=False),
    ]

    show_hidden = False
    ICON_NODE = ""
    ICON_NODE_EXPANDED = ""
    ICON_FILE = ""

    def filter_paths(self, paths):
        if self.show_hidden:
            return paths
        return [p for p in paths if not p.name.startswith(".")]

    def status_style(self, path: Path) -> str:
        """Hook for future git status colors. Return a rich style string."""
        return ""

    def render_label(self, node, base_style, style):
        label = super().render_label(node, base_style, style)
        if node.data is None:
            return label
        if node.allow_expand:
            glyph = FOLDER_OPEN if node.is_expanded else FOLDER_CLOSED
            color = "blue"
        else:
            glyph, color = file_icon(node.data.path.name)
        label = Text.assemble(Text(glyph + " ", style=color), label)
        if isinstance(label, Text):
            extra = self.status_style(node.data.path)
            if extra:
                label.stylize(extra)
        return label

    def action_pan(self, delta: int) -> None:
        self.scroll_to(x=max(0, self.scroll_x + delta), animate=False)

    def action_expand(self) -> None:
        node = self.cursor_node
        if node is not None and node.allow_expand and not node.is_expanded:
            node.expand()

    def action_collapse(self) -> None:
        node = self.cursor_node
        if node is None:
            return
        if node.allow_expand and node.is_expanded:
            node.collapse()
        elif node.parent is not None:
            self.move_cursor(node.parent)

    def on_tree_node_expanded(self, event) -> None:
        self.app.watch_dirs()

    def on_tree_node_collapsed(self, event) -> None:
        self.app.watch_dirs()

    def open_dirs(self) -> list[Path]:
        dirs = [Path(self.path)]
        stack = [self.root]
        while stack:
            n = stack.pop()
            for child in n.children:
                if child.is_expanded and child.data is not None:
                    dirs.append(child.data.path)
                    stack.append(child)
        return dirs

    def node_for(self, path: Path):
        if path == Path(self.path):
            return self.root
        stack = [self.root]
        while stack:
            n = stack.pop()
            for child in n.children:
                if child.data is not None:
                    if child.data.path == path:
                        return child
                    if child.is_expanded:
                        stack.append(child)
        return None


class Pf3(App):
    ENABLE_COMMAND_PALETTE = False
    CSS = """
    PathTree { background: transparent; padding: 0 1; }
    PathTree {
        scrollbar-size-vertical: 1;
        scrollbar-size-horizontal: 1;
        scrollbar-background: ansi_default;
        scrollbar-background-hover: ansi_default;
        scrollbar-background-active: ansi_default;
        scrollbar-corner-color: ansi_default;
        scrollbar-color: ansi_bright_black;
        scrollbar-color-hover: ansi_blue;
        scrollbar-color-active: ansi_cyan;
    }
    PathTree > .tree--cursor { background: ansi_blue; color: ansi_black; text-style: bold; }
    PathTree:focus > .tree--cursor { background: ansi_blue; color: ansi_black; text-style: bold; }
    PathTree > .tree--highlight { background: ansi_bright_black; }
    PathTree > .tree--highlight-line { background: ansi_bright_black; }
    PathTree > .directory-tree--folder { color: ansi_blue; text-style: bold; }
    Footer { background: transparent; }
    """
    BINDINGS = [
        Binding("full_stop,period,ctrl+h", "toggle_hidden", "Ocultos"),
        Binding("r", "reset", "Recolher tudo"),
        Binding("q", "quit", "Sair"),
    ]

    def __init__(self, root: Path):
        super().__init__(ansi_color=True)
        self.root_path = root
        self._watched: list[Path] = []

    def compose(self) -> ComposeResult:
        yield PathTree(self.root_path)
        yield Footer()

    def on_mount(self) -> None:
        tree = self.query_one(PathTree)
        tree.root.expand()
        tree.focus()
        self.title = str(self.root_path)
        self.watch_dirs()

    def action_reset(self) -> None:
        tree = self.query_one(PathTree)
        tree.root.collapse_all()
        tree.root.expand()
        tree.move_cursor(tree.root)

    def action_toggle_hidden(self) -> None:
        tree = self.query_one(PathTree)
        tree.show_hidden = not tree.show_hidden
        tree.reload()

    def on_directory_tree_directory_selected(self, event) -> None:
        event.stop()

    def on_directory_tree_file_selected(self, event) -> None:
        event.stop()

    def watch_dirs(self) -> None:
        tree = self.query_one(PathTree)
        dirs = sorted(d for d in tree.open_dirs() if d.is_dir())
        if dirs != self._watched:
            self._watched = dirs
            self._watch(dirs)

    @work(exclusive=True, group="watch")
    async def _watch(self, dirs: list[Path]) -> None:
        tree = self.query_one(PathTree)
        if not dirs:
            return
        async for changes in awatch(*dirs, recursive=False, debounce=300, yield_on_timeout=False):
            parents = {Path(p).parent for _, p in changes}
            for parent in parents:
                node = tree.node_for(parent)
                if node is not None:
                    tree.reload_node(node)


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else "."
    root = Path(arg).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"pf3: not a directory: {arg}")
    Pf3(root).run()


if __name__ == "__main__":
    main()

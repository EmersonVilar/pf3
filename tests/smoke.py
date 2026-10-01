"""Headless smoke test. Run: .venv/bin/python tests/smoke.py"""
import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pf3"))
import app as A  # noqa: E402


async def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "d").mkdir()
        (root / ".hid").touch()
        (root / "f.py").touch()
        pf3 = A.Pf3(root)
        async with pf3.run_test(size=(40, 12)) as pilot:
            tree = pf3.query_one(A.PathTree)
            await pilot.pause(0.5)
            names = lambda: [str(n.label) for n in tree.root.children]  # noqa: E731
            assert names() == ["d", "f.py"], names()
            await pilot.press("full_stop")
            await pilot.pause(0.3)
            assert ".hid" in names(), names()
            await pilot.press("j", "enter")
            await pilot.pause(0.5)
            (root / "d" / "new.txt").touch()
            await pilot.pause(1.5)
            assert [str(c.label) for c in tree.root.children[0].children] == ["new.txt"]
            await pilot.press("r")
            await pilot.pause(0.3)
            assert not tree.root.children[0].is_expanded
    assert A.file_icon("x.py")[0] != A.FILE_DEFAULT[0]
    assert A.file_icon("x.unknownext") == A.FILE_DEFAULT
    print("ok")


asyncio.run(main())

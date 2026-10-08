"""One entry point for rendering and showing the Manim Slides deck."""
from pathlib import Path
import argparse
import subprocess
import sys
import shutil
import webbrowser
from seminar import SCENES

ROOT = Path(__file__).resolve().parent
NAMES = [scene.__name__ for scene in SCENES]
SLIDES = shutil.which("manim-slides") or str(Path(sys.executable).with_name("manim-slides"))


def run(*args):
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["render", "present", "pngs", "html", "all"])
    parser.add_argument("--scene", choices=NAMES, help="Work on one scene")
    parser.add_argument("--draft", action="store_true",
                        help="480p render for quick visual checks")
    parser.add_argument("--native", action="store_true",
                        help="Use the Qt Manim Slides presenter (requires Qt bindings)")
    args = parser.parse_args()
    scenes = [args.scene] if args.scene else NAMES

    if args.command in ("render", "all"):
        render = [SLIDES, "render"]
        if args.draft:
            render.append("-ql")
        # Separate processes keep Manim's cache and video reversal bounded.
        for scene in scenes:
            run(*render, "seminar.py", scene)
    if args.command == "present":
        if args.native:
            try:
                import qtpy  # noqa: F401
            except ImportError:
                parser.error("Native presentation needs Qt bindings; install PySide6 or PyQt5 in this environment.")
            run(SLIDES, "present", *scenes)
        else:
            if args.scene:
                parser.error("--scene for presentation requires --native")
            run(sys.executable, "export_pngs.py", *scenes)
            run(sys.executable, "build_player.py")
            url = (ROOT / "outputs" / "seminar.html").as_uri()
            print(f"Open {url}")
            webbrowser.open(url)
    if args.command in ("pngs", "all"):
        run(sys.executable, "export_pngs.py", *scenes)
    if args.command in ("html", "all"):
        if args.scene:
            parser.error("html packaging requires the complete deck")
        run(sys.executable, "build_player.py")


if __name__ == "__main__":
    main()

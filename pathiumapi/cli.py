import argparse
import os
import sys
import textwrap
from pathlib import Path



def new_project(name: str) -> None:
    root = Path(name)
    if root.exists():
        print(f"Folder {name} already exists")
        return
    root.mkdir(parents=True)
    (root / "app.py").write_text(textwrap.dedent(f"""
        from pathiumapi import Pathium, Response

        app = Pathium()

        @app.get("/")
        async def index(req):
            return Response("Hello from {name}")

    """))
    (root / "README.md").write_text(f"# {name}\n\nA PathiumAPI app created by `pathiumapi new`\n")
    print(f"Created project {name}")


def run_app(path: str = ".") -> None:
    # Try to find an ASGI app in examples/app.py or app.py
    p = Path(path)
    candidates = [p / "app.py", p / "examples" / "app.py"]
    target = None
    for c in candidates:
        if c.exists():
            target = c
            break
    if target is None:
        print("No app.py found in the current folder or examples/. Create one with `pathiumapi new <name>`." )
        return

    # Attempt to run with uvicorn if available
    try:
        import uvicorn
    except Exception:
        print("Install uvicorn to run the app: pip install uvicorn")
        return

    # derive module path like examples.app or app
    try:
        # Try to compute a module path relative to the current working directory
        rel = target.relative_to(Path.cwd())
        module = ".".join(rel.with_suffix("").parts)
    except Exception:
        # If the target is not inside CWD (or relative_to fails), fall back to
        # adding the app's parent directory to sys.path and importing by name.
        module = target.with_suffix("").name
        import sys
        sys.path.insert(0, str(target.parent.resolve()))

    print(f"Running {module}:app with uvicorn")
    uvicorn.run(f"{module}:app", host="127.0.0.1", port=8000)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pathiumapi", description="PathiumAPI developer CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_new = sub.add_parser("new", help="Create a new PathiumAPI app scaffold")
    p_new.add_argument("name")

    p_run = sub.add_parser("run", help="Run a PathiumAPI app in the current folder")
    p_run.add_argument("path", nargs="?", default=".")

    args = parser.parse_args(argv)
    if args.cmd == "new":
        new_project(args.name)
    elif args.cmd == "run":
        run_app(args.path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

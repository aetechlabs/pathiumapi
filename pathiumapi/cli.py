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
    else:
        tpl = textwrap.dedent(f"""
            from pathiumapi import Response

            def register(app):
                @app.{method}("{route_path}")
                async def {name}(req):
                    return Response.json({{"message": "Hello from {name}", "path": "{route_path}"}})

        """)
        target.write_text(tpl)
        print(f"Created route stub: {target}")
        # adding the app's parent directory to sys.path and importing by name.
        module = target.with_suffix("").name
        import sys
        sys.path.insert(0, str(target.parent.resolve()))

    print(f"Running {module}:app with uvicorn")
    uvicorn.run(f"{module}:app", host="127.0.0.1", port=8000)


def generate_route(name: str, route_path: str, method: str = "get", app_file: str = "app.py") -> None:
    """Generate a simple route stub under `routes/<name>.py` and try to register it in `app_file`.

    The generated file contains a `register(app)` helper so users can import
    and attach the routes to their `Pathium` instance.
    """
    routes_dir = Path("routes")
    routes_dir.mkdir(exist_ok=True)
    target = routes_dir / f"{name}.py"
    if target.exists():
        # If the file exists, try to add another method handler into the
        # existing `def register(app):` block rather than failing outright.
        content = target.read_text()
        # If the exact decorator (method+path) already exists, bail out.
        if f'@app.{method}("{route_path}")' in content:
            print(f"Route file {target} already contains this route")
            return

        # Build a handler name that includes the method to avoid name collisions
        handler_name = f"{name}_{method}"
        if f"def {handler_name}(req)" in content or f"async def {handler_name}(req)" in content:
            print(f"Route file {target} already contains a handler named {handler_name}")
            return

        new_handler = textwrap.dedent(f'''
            \n
                @app.{method}("{route_path}")
                async def {handler_name}(req):
                    return Response.json({{"message": "Hello from {name}", "path": "{route_path}", "method": "{method.upper()}"}})

        ''')

        # Insert the new handler inside the existing `def register(app):` block if present.
        lines = content.splitlines(keepends=True)
        reg_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("def register(app):"):
                reg_idx = i
                break

        if reg_idx is None:
            # No register function found — append a new register function at EOF
            tpl = textwrap.dedent(f"""
                \n
                def register(app):
                    @app.{method}("{route_path}")
                    async def {handler_name}(req):
                        return Response.json({{"message": "Hello from {name}", "path": "{route_path}", "method": "{method.upper()}"}})

            """)
            with target.open("a", encoding="utf-8") as fh:
                fh.write(tpl)
            print(f"Appended handler for {method.upper()} to {target}")
            # Try to auto-register in app_file later (existing logic handles app_file)
        else:
            # Find end of the register block: first subsequent line with no leading whitespace
            end_idx = len(lines)
            for j in range(reg_idx + 1, len(lines)):
                l = lines[j]
                if l.strip() == "":
                    continue
                # If this line has no indentation (starts at column 0), it's outside the block
                if l[:len(l) - len(l.lstrip())] == "":
                    end_idx = j
                    break

            # Insert new handler just before end_idx, ensure proper indentation
            lines.insert(end_idx, new_handler)
            target.write_text("".join(lines))
            print(f"Inserted handler for {method.upper()} into {target}")
        # Don't create a new file — we've updated the existing file instead.
        # Attempt to append registration to app_file below if needed.
    else:

        tpl = textwrap.dedent(f"""
            from pathiumapi import Response

            def register(app):
                @app.{method}("{route_path}")
                async def {name}(req):
                    return Response.json({{"message": "Hello from {name}", "path": "{route_path}"}})

        """
        )
    target.write_text(tpl)
    print(f"Created route stub: {target}")

    # Try to append auto-registration into app_file if it exists and doesn't already
    app_path = Path(app_file)
    if app_path.exists():
        content = app_path.read_text()
        import_line = f"\n# Auto-imported route generated by pathiumapi CLI\nfrom routes import {name} as {name}_module\n{name}_module.register(app)\n"
        if import_line.strip() in content:
            print(f"{app_file} already references the generated route")
        else:
            with app_path.open("a", encoding="utf-8") as fh:
                fh.write(import_line)
            print(f"Appended registration to {app_file}")
    else:
        print(f"Tip: import and call `register(app)` from {target} in your application file.")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pathiumapi", description="PathiumAPI developer CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_new = sub.add_parser("new", help="Create a new PathiumAPI app scaffold")
    p_new.add_argument("name")

    p_run = sub.add_parser("run", help="Run a PathiumAPI app in the current folder")
    p_run.add_argument("path", nargs="?", default=".")

    p_gen = sub.add_parser("generate", help="Generate scaffolding (routes, middleware, etc.)")
    p_gen_sub = p_gen.add_subparsers(dest="what")

    p_gen_route = p_gen_sub.add_parser("route", help="Generate a route stub")
    p_gen_route.add_argument("name", help="Name for the route file/function (e.g. users)")
    p_gen_route.add_argument("--path", dest="route_path", required=True, help="HTTP path for the route (e.g. /users)")
    p_gen_route.add_argument("--method", dest="method", default="get", help="HTTP method (get, post, put, delete)")
    p_gen_route.add_argument("--app-file", dest="app_file", default="app.py", help="Application file to auto-register the route (optional)")

    args = parser.parse_args(argv)
    if args.cmd == "new":
        new_project(args.name)
    elif args.cmd == "run":
        run_app(args.path)
    elif args.cmd == "generate":
        if getattr(args, "what", None) == "route":
            generate_route(args.name, args.route_path, args.method, args.app_file)
        else:
            print("Specify what to generate. Available: route")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

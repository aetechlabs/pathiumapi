import warnings

warnings.warn(
    "The 'lilac.cli' module is deprecated — use 'pathiumapi.cli' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from pathiumapi.cli import new_project, run_app, main

__all__ = ["new_project", "run_app", "main"]

if __name__ == "__main__":
    main()

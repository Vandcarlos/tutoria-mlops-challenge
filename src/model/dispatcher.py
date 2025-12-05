"""
Model container dispatcher.

This script reads STEP_NAME from environment variables (or CLI args)
and dispatches execution to the correct Python module inside the image.

Usage examples:
- STEP_NAME=ingest python -m src.model.pipeline.dispatcher
- python -m src.model.pipeline.dispatcher ingest
"""

from __future__ import annotations

import os
import subprocess
import sys

# Mapping between step names and Python modules
STEP_TO_MODULE: dict[str, str] = {
    # Data steps
    "ingest": "src.model.data.ingest",
    "split_batches": "src.model.data.split_batches",
    # Training / evaluation steps
    "preprocess_batch": "src.model.pipeline.preprocess_batch",
    "train": "src.model.pipeline.train",
    "evaluate": "src.model.pipeline.evaluate",
}


def resolve_step_name() -> str:
    """
    Resolve step name from CLI args or environment variable.

    Priority:
    1) First CLI argument: python -m ... <STEP_NAME>
    2) STEP_NAME environment variable

    Raises:
        SystemExit: if no step name was provided.
    """
    # 1) CLI arg
    if len(sys.argv) > 1:
        return sys.argv[1]

    # 2) Environment variable
    step_name = os.getenv("STEP_NAME")
    if step_name:
        return step_name

    print(
        "[dispatcher] ERROR: STEP_NAME not provided. "
        "Use CLI arg or set STEP_NAME env var."
    )
    print("[dispatcher] Example:")
    print("  STEP_NAME=ingest python -m src.model.pipeline.dispatcher")
    sys.exit(1)


def get_module_for_step(step_name: str) -> str:
    """
    Get Python module for a given step name.

    Args:
        step_name: logical step name (e.g., 'ingest', 'train').

    Returns:
        The full Python module path.

    Raises:
        SystemExit: if step name is unknown.
    """
    module = STEP_TO_MODULE.get(step_name)
    if module is None:
        valid = ", ".join(sorted(STEP_TO_MODULE.keys()))
        print(f"[dispatcher] ERROR: Unknown STEP_NAME='{step_name}'.")
        print(f"[dispatcher] Valid values are: {valid}")
        sys.exit(1)

    return module


def run_module(module: str) -> None:
    """
    Run a Python module as 'python -m <module>'.

    All environment variables are preserved.
    CLI args after STEP_NAME are forwarded to the module.
    """
    extra_args = sys.argv[2:] if len(sys.argv) > 2 else []

    cmd = ["python", "-m", module, *extra_args]

    print(f"[dispatcher] Running module: {module}")
    print(f"[dispatcher] Command: {' '.join(cmd)}")

    # Use check=True to fail the container if the step fails
    subprocess.run(cmd, check=True)


def main() -> None:
    """Main entrypoint for the dispatcher."""
    step_name = resolve_step_name()
    module = get_module_for_step(step_name)
    run_module(module)


if __name__ == "__main__":
    main()

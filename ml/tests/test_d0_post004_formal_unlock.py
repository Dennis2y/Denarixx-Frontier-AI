from __future__ import annotations

import ast
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

MODULE_PATH = (
    ROOT
    / "ml"
    / "evaluation"
    / "d0_post004_formal_unlock.py"
)

spec = importlib.util.spec_from_file_location(
    "d0_post004_formal_unlock",
    MODULE_PATH,
)

assert spec is not None
assert spec.loader is not None

unlock = importlib.util.module_from_spec(spec)
spec.loader.exec_module(unlock)


def test_preflight_is_non_scoring():
    result = unlock.preflight()

    assert result["formalScoringExecuted"] is False
    assert result["frozenInputsVerified"] is True
    assert result["exposureMarkerExists"] is False


def test_begin_exposure_not_called_by_preflight():
    assert not unlock.EXPOSURE_MARKER.exists()


def test_source_contains_no_model_scoring():
    source = MODULE_PATH.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(source)

    forbidden_calls = {
        "evaluate_checkpoint",
        "response_loss_for_example",
        "greedy_generate",
        "forward",
        "backward",
        "step",
    }

    found = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func

        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        else:
            continue

        if name in forbidden_calls:
            found.add(name)

    assert not found, found


def test_no_torch_import():
    source = MODULE_PATH.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name != "torch"

        if isinstance(node, ast.ImportFrom):
            assert node.module != "torch"


def test_exclusive_marker_creation_present():
    source = MODULE_PATH.read_text(
        encoding="utf-8"
    )

    assert '.open(' in source
    assert '"x"' in source


if __name__ == "__main__":
    tests = [
        test_preflight_is_non_scoring,
        test_begin_exposure_not_called_by_preflight,
        test_source_contains_no_model_scoring,
        test_no_torch_import,
        test_exclusive_marker_creation_present,
    ]

    for test in tests:
        test()
        print(f"✓ {test.__name__}")

    print()
    print(
        "All POST-004 one-time unlock "
        "synthetic tests passed."
    )

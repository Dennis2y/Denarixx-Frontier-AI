from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ml.evaluation.d0_post008_execution_harness import (
    HarnessIdentities,
    HarnessPaths,
    RealPathCollisionError,
    RerunError,
    TopologyError,
    run_real_formal_execution,
    run_synthetic_lifecycle,
)


class FakeDependencies:
    def __init__(
        self,
        *,
        fail_at: str | None = None,
    ):
        self.events: list[str] = []
        self.fail_at = fail_at

    def load_rows(self, dataset: Path):
        self.events.append("load_rows")

        if self.fail_at == "load_rows":
            raise RuntimeError(
                "injected load failure"
            )

        return [
            {
                "instruction": "synthetic",
                "response": "synthetic",
            }
        ]

    def score_checkpoint(
        self,
        checkpoint: Path,
        rows,
    ):
        del rows

        name = checkpoint.name

        if "baseline" in name:
            event = "score_baseline"
        else:
            event = "score_candidate"

        self.events.append(event)

        if self.fail_at == event:
            raise RuntimeError(
                f"injected {event} failure"
            )

        return {
            "checkpoint": name,
            "score": (
                1.0
                if event == "score_baseline"
                else 2.0
            ),
        }

    def compare_results(
        self,
        baseline,
        candidate,
    ):
        self.events.append("compare")

        if self.fail_at == "compare":
            raise RuntimeError(
                "injected comparison failure"
            )

        return {
            "baselineScore": baseline["score"],
            "candidateScore": candidate["score"],
            "decision": "synthetic-pass",
        }


def sha256_file(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def make_paths(
    tmp_path: Path,
) -> HarnessPaths:
    dataset = tmp_path / "dataset.synthetic.jsonl"
    baseline = tmp_path / "baseline.synthetic.pt"
    candidate = tmp_path / "candidate.synthetic.pt"

    dataset.write_text(
        '{"synthetic": true}\n',
        encoding="utf-8",
    )
    baseline.write_bytes(b"synthetic-baseline")
    candidate.write_bytes(b"synthetic-candidate")

    result_dir = tmp_path / "result"

    return HarnessPaths(
        dataset=dataset,
        baseline=baseline,
        candidate=candidate,
        exposure_marker=(
            result_dir /
            "FORMAL_EXPOSURE_STARTED"
        ),
        result_dir=result_dir,
    )


def identities(
    paths: HarnessPaths,
) -> HarnessIdentities:
    return HarnessIdentities(
        dataset_sha256=sha256_file(
            paths.dataset
        ),
        baseline_sha256=sha256_file(
            paths.baseline
        ),
        candidate_sha256=sha256_file(
            paths.candidate
        ),
    )


def test_exact_real_topology_completes(
    tmp_path: Path,
):
    paths = make_paths(tmp_path)
    deps = FakeDependencies()

    result = run_synthetic_lifecycle(
        paths=paths,
        dependencies=deps,
        expected_identities=identities(paths),
    )

    assert result["status"] == "completed"

    assert (
        paths.exposure_marker.parent.resolve()
        == paths.result_dir.resolve()
    )

    assert paths.exposure_marker.is_file()

    assert (
        paths.result_dir /
        "BASELINE_RESULT.json"
    ).is_file()

    assert (
        paths.result_dir /
        "CANDIDATE_RESULT.json"
    ).is_file()

    assert (
        paths.result_dir /
        "FINAL_ADJUDICATION.json"
    ).is_file()

    assert deps.events == [
        "load_rows",
        "score_baseline",
        "score_candidate",
        "compare",
    ]


def test_post007_fileexists_regression(
    tmp_path: Path,
):
    """
    This exact topology would have triggered the POST-007 defect.

    Exposure marker creation necessarily establishes result_dir.
    The corrected lifecycle must continue without trying to create
    result_dir again with exist_ok=False.
    """

    paths = make_paths(tmp_path)

    run_synthetic_lifecycle(
        paths=paths,
        dependencies=FakeDependencies(),
        expected_identities=identities(paths),
    )

    assert paths.result_dir.is_dir()
    assert paths.exposure_marker.is_file()


def test_baseline_persisted_before_candidate_scoring(
    tmp_path: Path,
):
    paths = make_paths(tmp_path)

    class InspectingDependencies(FakeDependencies):
        def score_checkpoint(
            self,
            checkpoint: Path,
            rows,
        ):
            if "candidate" in checkpoint.name:
                baseline_path = (
                    paths.result_dir /
                    "BASELINE_RESULT.json"
                )

                assert baseline_path.is_file()

            return super().score_checkpoint(
                checkpoint,
                rows,
            )

    run_synthetic_lifecycle(
        paths=paths,
        dependencies=InspectingDependencies(),
        expected_identities=identities(paths),
    )


def test_comparator_consumes_persisted_results(
    tmp_path: Path,
):
    paths = make_paths(tmp_path)

    class PersistedInspectingDependencies(
        FakeDependencies
    ):
        def compare_results(
            self,
            baseline,
            candidate,
        ):
            persisted_baseline = json.loads(
                (
                    paths.result_dir /
                    "BASELINE_RESULT.json"
                ).read_text(encoding="utf-8")
            )

            persisted_candidate = json.loads(
                (
                    paths.result_dir /
                    "CANDIDATE_RESULT.json"
                ).read_text(encoding="utf-8")
            )

            assert baseline == persisted_baseline
            assert candidate == persisted_candidate

            return super().compare_results(
                baseline,
                candidate,
            )

    run_synthetic_lifecycle(
        paths=paths,
        dependencies=(
            PersistedInspectingDependencies()
        ),
        expected_identities=identities(paths),
    )


def test_second_lifecycle_rejected(
    tmp_path: Path,
):
    paths = make_paths(tmp_path)

    run_synthetic_lifecycle(
        paths=paths,
        dependencies=FakeDependencies(),
        expected_identities=identities(paths),
    )

    with pytest.raises(RerunError):
        run_synthetic_lifecycle(
            paths=paths,
            dependencies=FakeDependencies(),
            expected_identities=identities(paths),
        )


def test_preexisting_result_directory_rejected(
    tmp_path: Path,
):
    paths = make_paths(tmp_path)

    paths.result_dir.mkdir()

    with pytest.raises(RerunError):
        run_synthetic_lifecycle(
            paths=paths,
            dependencies=FakeDependencies(),
            expected_identities=identities(paths),
        )


def test_preexisting_exposure_marker_rejected(
    tmp_path: Path,
):
    paths = make_paths(tmp_path)

    paths.result_dir.mkdir()
    paths.exposure_marker.write_text(
        "existing\n",
        encoding="utf-8",
    )

    with pytest.raises(RerunError):
        run_synthetic_lifecycle(
            paths=paths,
            dependencies=FakeDependencies(),
            expected_identities=identities(paths),
        )


def test_wrong_topology_rejected(
    tmp_path: Path,
):
    paths = make_paths(tmp_path)

    wrong = HarnessPaths(
        dataset=paths.dataset,
        baseline=paths.baseline,
        candidate=paths.candidate,
        exposure_marker=(
            tmp_path /
            "different-parent" /
            "FORMAL_EXPOSURE_STARTED"
        ),
        result_dir=paths.result_dir,
    )

    with pytest.raises(TopologyError):
        run_synthetic_lifecycle(
            paths=wrong,
            dependencies=FakeDependencies(),
            expected_identities=identities(paths),
        )


def test_failure_after_exposure_is_persisted(
    tmp_path: Path,
):
    paths = make_paths(tmp_path)

    with pytest.raises(RuntimeError):
        run_synthetic_lifecycle(
            paths=paths,
            dependencies=FakeDependencies(
                fail_at="score_candidate"
            ),
            expected_identities=identities(paths),
        )

    assert paths.exposure_marker.is_file()

    assert (
        paths.result_dir /
        "BASELINE_RESULT.json"
    ).is_file()

    failure_path = (
        paths.result_dir /
        "FAILURE.json"
    )

    assert failure_path.is_file()

    failure = json.loads(
        failure_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        failure["status"]
        == "failed-after-synthetic-exposure"
    )


def test_failure_does_not_overwrite_prior_evidence(
    tmp_path: Path,
):
    paths = make_paths(tmp_path)

    with pytest.raises(RuntimeError):
        run_synthetic_lifecycle(
            paths=paths,
            dependencies=FakeDependencies(
                fail_at="score_candidate"
            ),
            expected_identities=identities(paths),
        )

    baseline_path = (
        paths.result_dir /
        "BASELINE_RESULT.json"
    )

    before = baseline_path.read_bytes()

    with pytest.raises(RerunError):
        run_synthetic_lifecycle(
            paths=paths,
            dependencies=FakeDependencies(),
            expected_identities=identities(paths),
        )

    assert baseline_path.read_bytes() == before


def test_reserved_real_result_path_rejected(
    tmp_path: Path,
):
    paths = make_paths(tmp_path)

    real_result_dir = Path(
        "local-evidence/d0-post008-formal-execution"
    )

    colliding = HarnessPaths(
        dataset=paths.dataset,
        baseline=paths.baseline,
        candidate=paths.candidate,
        exposure_marker=(
            real_result_dir /
            "FORMAL_EXPOSURE_STARTED"
        ),
        result_dir=real_result_dir,
    )

    with pytest.raises(RealPathCollisionError):
        run_synthetic_lifecycle(
            paths=colliding,
            dependencies=FakeDependencies(),
            expected_identities=identities(paths),
        )


def test_real_formal_execution_disabled():
    with pytest.raises(Exception):
        run_real_formal_execution()

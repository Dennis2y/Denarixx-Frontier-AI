"""Controlled local research corpus for Denarixx D0 experiments.

This corpus is generated from original Denarixx-authored templates and
contains no scraped third-party material. It exists to provide a larger,
deterministic development dataset for architecture experiments.

It is NOT intended to be production pretraining data.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


CONCEPTS = [
    "reasoning",
    "mathematics",
    "coding",
    "science",
    "language",
    "memory",
    "planning",
    "verification",
    "efficiency",
    "reliability",
    "uncertainty",
    "prediction",
    "evaluation",
    "optimization",
    "learning",
    "attention",
    "representation",
    "generalization",
    "inference",
    "training",
]

QUALITIES = [
    "accurate",
    "efficient",
    "reproducible",
    "measurable",
    "robust",
    "careful",
    "transparent",
    "testable",
    "consistent",
    "evidence-driven",
]

ACTIONS = [
    "measure",
    "compare",
    "verify",
    "evaluate",
    "analyze",
    "improve",
    "test",
    "record",
    "challenge",
    "validate",
]

TEMPLATES = [
    "Denarixx studies {concept} through {quality} experiments.",
    "A strong research system must {action} {concept} with controlled evidence.",
    "The D0 program treats {concept} as a measurable research problem.",
    "Before scaling {concept}, researchers must {action} the baseline.",
    "Reliable artificial intelligence requires {quality} {concept}.",
    "Every experiment should {action} whether {concept} improved.",
    "Research conclusions about {concept} must remain {quality}.",
    "Denarixx records negative results when {concept} does not improve.",
    "Compute should increase only after researchers {action} useful gains in {concept}.",
    "A model is not better merely because its {concept} system is larger.",
]


def build_research_corpus() -> str:
    lines: list[str] = []

    for concept_index, concept in enumerate(CONCEPTS):
        for quality_index, quality in enumerate(QUALITIES):
            action = ACTIONS[
                (concept_index + quality_index) % len(ACTIONS)
            ]

            for template_index, template in enumerate(TEMPLATES):
                if (
                    template_index
                    + concept_index
                    + quality_index
                ) % 3 != 0:
                    continue

                lines.append(
                    template.format(
                        concept=concept,
                        quality=quality,
                        action=action,
                    )
                )

    reasoning_examples = [
        "If every verified result is reproducible and experiment A is verified, then experiment A should be reproducible.",
        "If validation loss decreases while the evaluation protocol remains fixed, the result is evidence of improved predictive fit on that validation set.",
        "A lower training loss alone does not prove better generalization.",
        "A larger parameter count alone does not prove greater intelligence.",
        "When two architectures use different compute budgets, their raw scores are not a controlled efficiency comparison.",
        "When a benchmark appears in training data, the benchmark may no longer provide a clean measure of generalization.",
        "An experiment with one random seed can be informative but is weaker evidence than consistent results across several seeds.",
        "If a new architecture is slower and less accurate than the baseline under equal conditions, Denarixx should reject that variant.",
        "If a new architecture improves accuracy but doubles compute, researchers must report both the capability gain and the efficiency cost.",
        "Scientific progress requires recording failures as well as successes.",
    ]

    lines.extend(reasoning_examples * 20)

    return "\n".join(lines) + "\n"


def ensure_research_corpus(path: Path) -> dict:
    text = build_research_corpus()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

    digest = hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

    return {
        "path": str(path),
        "sha256": digest,
        "characters": len(text),
        "words": len(text.split()),
        "lines": len(text.splitlines()),
        "provenance": (
            "Deterministically generated from original "
            "Denarixx-authored research templates."
        ),
    }


if __name__ == "__main__":
    target = (
        Path(__file__).parent
        / "d0_research_corpus.txt"
    )

    metadata = ensure_research_corpus(target)

    for key, value in metadata.items():
        print(f"{key}: {value}")

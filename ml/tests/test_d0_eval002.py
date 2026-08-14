from pathlib import Path
import json
import hashlib

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "ml" / "data"

LM2 = DATA / "d0_eval002_lm.txt"
INST2 = DATA / "d0_eval002_instructions.jsonl"

PRETRAIN = DATA / "d0_research_corpus.txt"
SFT = DATA / "d0_sft_tiny.jsonl"
LM1 = DATA / "d0_eval001_lm.txt"
INST1 = DATA / "d0_eval001_instructions.jsonl"


def load_jsonl(path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def normalized(text):
    return " ".join(text.lower().split())


def test_eval002_files_exist():
    assert LM2.is_file()
    assert INST2.is_file()


def test_eval002_lm_has_expected_scale():
    lines = [
        x.strip()
        for x in LM2.read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    assert len(lines) >= 40
    assert len(set(lines)) == len(lines)


def test_eval002_instruction_has_expected_scale():
    rows = load_jsonl(INST2)
    assert len(rows) >= 20

    for row in rows:
        assert isinstance(row.get("instruction"), str)
        assert isinstance(row.get("response"), str)
        assert row["instruction"].strip()
        assert row["response"].strip()


def test_eval002_lm_not_exactly_in_pretraining():
    training = normalized(PRETRAIN.read_text(encoding="utf-8"))

    for line in LM2.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            assert normalized(line) not in training


def test_eval002_lm_distinct_from_eval001():
    eval1 = {
        normalized(x)
        for x in LM1.read_text(encoding="utf-8").splitlines()
        if x.strip()
    }

    for line in LM2.read_text(encoding="utf-8").splitlines():
        if line.strip():
            assert normalized(line) not in eval1


def test_eval002_instructions_not_in_sft():
    sft_text = normalized(SFT.read_text(encoding="utf-8"))

    for row in load_jsonl(INST2):
        assert normalized(row["instruction"]) not in sft_text
        assert normalized(row["response"]) not in sft_text


def test_eval002_instructions_distinct_from_eval001():
    old = load_jsonl(INST1)

    old_instructions = {
        normalized(x["instruction"])
        for x in old
    }

    old_responses = {
        normalized(x["response"])
        for x in old
    }

    for row in load_jsonl(INST2):
        assert normalized(row["instruction"]) not in old_instructions
        assert normalized(row["response"]) not in old_responses


def test_eval002_hash_shape():
    for path in (LM2, INST2):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert len(digest) == 64
        int(digest, 16)


def test_eval002_has_no_duplicate_instruction_pairs():
    rows = load_jsonl(INST2)

    pairs = [
        (
            normalized(x["instruction"]),
            normalized(x["response"]),
        )
        for x in rows
    ]

    assert len(pairs) == len(set(pairs))

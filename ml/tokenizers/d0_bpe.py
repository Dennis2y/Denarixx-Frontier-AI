"""Denarixx D0 experimental BPE tokenizer.

The tokenizer vocabulary is trained locally from Denarixx-controlled
text. No pretrained tokenizer vocabulary or model is downloaded.
"""

from __future__ import annotations

import json
from pathlib import Path

from tokenizers import Tokenizer
from tokenizers.decoders import ByteLevel as ByteLevelDecoder
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.trainers import BpeTrainer


SPECIAL_TOKENS = [
    "<pad>",
    "<unk>",
    "<bos>",
    "<eos>",
]


class D0BPETokenizer:
    """Small reproducible BPE tokenizer for the D0.3 experiment."""

    def __init__(self, tokenizer: Tokenizer):
        self._tokenizer = tokenizer

    @classmethod
    def train(
        cls,
        text: str,
        vocab_size: int = 64,
        min_frequency: int = 1,
    ) -> "D0BPETokenizer":
        if not text:
            raise ValueError("cannot train tokenizer on empty text")

        if vocab_size <= len(SPECIAL_TOKENS):
            raise ValueError(
                "vocab_size must exceed the number of special tokens"
            )

        tokenizer = Tokenizer(
            BPE(
                unk_token="<unk>",
            )
        )

        tokenizer.pre_tokenizer = ByteLevel(
            add_prefix_space=False,
        )

        tokenizer.decoder = ByteLevelDecoder()

        trainer = BpeTrainer(
            vocab_size=vocab_size,
            min_frequency=min_frequency,
            special_tokens=SPECIAL_TOKENS,
            show_progress=False,
        )

        tokenizer.train_from_iterator(
            [text],
            trainer=trainer,
            length=1,
        )

        return cls(tokenizer)

    @property
    def vocab_size(self) -> int:
        return self._tokenizer.get_vocab_size()

    def encode(self, text: str) -> list[int]:
        return self._tokenizer.encode(text).ids

    def decode(self, tokens: list[int]) -> str:
        return self._tokenizer.decode(
            tokens,
            skip_special_tokens=True,
        )

    def vocabulary(self) -> dict[str, int]:
        return dict(
            sorted(
                self._tokenizer.get_vocab().items(),
                key=lambda item: item[1],
            )
        )

    def to_json(self) -> str:
        return self._tokenizer.to_str()

    def save(self, path: Path) -> None:
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        path.write_text(
            self.to_json(),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> "D0BPETokenizer":
        return cls(
            Tokenizer.from_str(
                path.read_text(encoding="utf-8")
            )
        )

    def metadata(self) -> dict:
        return {
            "type": "bpe",
            "implementation": "huggingface-tokenizers",
            "vocabSize": self.vocab_size,
            "specialTokens": list(SPECIAL_TOKENS),
            "vocabulary": self.vocabulary(),
        }

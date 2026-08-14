"""A deterministic local-development character tokenizer."""

from dataclasses import dataclass


@dataclass
class CharacterTokenizer:
    alphabet: list[str]

    @classmethod
    def train(cls, text: str) -> "CharacterTokenizer":
        alphabet = sorted(set(text))
        if not alphabet:
            raise ValueError("cannot train tokenizer on empty text")
        return cls(alphabet=alphabet)

    @property
    def vocab_size(self) -> int:
        return len(self.alphabet)

    def encode(self, text: str) -> list[int]:
        lookup = {token: index for index, token in enumerate(self.alphabet)}
        unknown = lookup[self.alphabet[0]]
        return [lookup.get(character, unknown) for character in text]

    def decode(self, tokens: list[int]) -> str:
        return "".join(self.alphabet[index] for index in tokens)

    def to_dict(self) -> dict[str, list[str]]:
        return {"alphabet": self.alphabet}

    @classmethod
    def from_dict(cls, payload: dict[str, list[str]]) -> "CharacterTokenizer":
        return cls(alphabet=payload["alphabet"])
"""Caption text policy and contextual correction engine.

The first policy layer is intentionally small and testable. It captures the
real revision patterns from production caption QA: ASR homophones, model-name
casing, missing function words, grammar repair, and spoken acronym timing.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import re
from typing import Iterable, Sequence


TRAILING_PUNCT = "!?;,:"
SPOKEN_ACRONYMS = {"api", "css", "gpu", "html", "lora", "nfa", "seo", "ui", "ux", "vram"}


@dataclass(frozen=True)
class CaptionToken:
    text: str
    start: float | None = None
    end: float | None = None
    source_text: str | None = None
    flags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CorrectionDecision:
    category: str
    original: str
    replacement: str
    reason: str
    confidence: float
    span_start: int
    span_end: int


@dataclass(frozen=True)
class PolicyResult:
    tokens: tuple[CaptionToken, ...]
    decisions: tuple[CorrectionDecision, ...]

    @property
    def text(self) -> str:
        return " ".join(token.text for token in self.tokens if token.text)

    def caption_text(self, uppercase: bool = True) -> str:
        text = self.text
        return text.upper() if uppercase else text


@dataclass(frozen=True)
class PhraseRule:
    match: tuple[str, ...]
    replacement: tuple[str, ...]
    category: str
    reason: str
    confidence: float = 0.95


PHRASE_RULES: tuple[PhraseRule, ...] = (
    PhraseRule(
        ("exacting", "2.0"),
        ("exciting", "as", "Seedance", "2.0"),
        "contextual_model_name",
        "The AI video model context makes this phrase read as Seedance 2.0, not exacting 2.0.",
        0.92,
    ),
    PhraseRule(
        ("c", "dance", "2.0"),
        ("Seedance", "2.0"),
        "contextual_model_name",
        "ASR often hears Seedance as C dance.",
    ),
    PhraseRule(
        ("sea", "dance", "2.0"),
        ("Seedance", "2.0"),
        "contextual_model_name",
        "ASR often hears Seedance as sea dance.",
    ),
    PhraseRule(
        ("low", "raw"),
        ("LoRA",),
        "domain_term",
        "In model-training context, low raw is almost always LoRA.",
    ),
    PhraseRule(
        ("low", "ra"),
        ("LoRA",),
        "domain_term",
        "In model-training context, low ra is almost always LoRA.",
    ),
    PhraseRule(
        ("low-ra",),
        ("LoRA",),
        "domain_term",
        "Hyphenated ASR approximation should normalize to LoRA.",
    ),
    PhraseRule(
        ("lora",),
        ("LoRA",),
        "domain_term",
        "Canonical casing for LoRA.",
    ),
    PhraseRule(
        ("what", "is", "this", "unlock"),
        ("what", "does", "this", "unlock"),
        "grammar_repair",
        "The idiomatic question is what does this unlock.",
    ),
    PhraseRule(
        ("sticking", "the", "30"),
        ("sticking", "to", "30"),
        "idiom_repair",
        "The intended phrase is sticking to 30 frames a second.",
    ),
    PhraseRule(
        ("calm", "the", "fuckdown"),
        ("calm", "the", "fuck", "down"),
        "token_split",
        "Profanity-adjacent joined token should be split when the sentence clearly says calm the fuck down.",
        0.9,
    ),
)


def as_tokens(words: Sequence[str | CaptionToken]) -> tuple[CaptionToken, ...]:
    tokens: list[CaptionToken] = []
    for word in words:
        if isinstance(word, CaptionToken):
            tokens.append(word)
        else:
            tokens.append(CaptionToken(text=str(word), source_text=str(word)))
    return tuple(tokens)


def split_trailing_punctuation(text: str) -> tuple[str, str]:
    base = text
    punct = ""
    while base and base[-1] in TRAILING_PUNCT:
        punct = base[-1] + punct
        base = base[:-1]
    if base.endswith(".") and not re.search(r"\d\.\d$", base):
        punct = "." + punct
        base = base[:-1]
    return base, punct


def normalized_base(text: str) -> str:
    base, _ = split_trailing_punctuation(text.strip())
    return base.lower()


def append_final_punctuation(words: list[str], source_tokens: Sequence[CaptionToken]) -> list[str]:
    if not words:
        return words
    _, punct = split_trailing_punctuation(source_tokens[-1].text)
    if punct and not words[-1].endswith(tuple(TRAILING_PUNCT + ".")):
        words[-1] = f"{words[-1]}{punct}"
    return words


def distribute_timing(source_tokens: Sequence[CaptionToken], count: int) -> list[tuple[float | None, float | None]]:
    if count <= 0:
        return []
    first = source_tokens[0]
    last = source_tokens[-1]
    if first.start is None or last.end is None or last.end <= first.start:
        return [(None, None) for _ in range(count)]
    duration = (last.end - first.start) / count
    return [(first.start + duration * i, first.start + duration * (i + 1)) for i in range(count)]


def apply_phrase_rules(tokens: tuple[CaptionToken, ...]) -> tuple[tuple[CaptionToken, ...], tuple[CorrectionDecision, ...]]:
    output: list[CaptionToken] = []
    decisions: list[CorrectionDecision] = []
    rules = sorted(PHRASE_RULES, key=lambda rule: len(rule.match), reverse=True)
    i = 0
    while i < len(tokens):
        matched: PhraseRule | None = None
        matched_source: tuple[CaptionToken, ...] = ()
        for rule in rules:
            source = tokens[i : i + len(rule.match)]
            if len(source) != len(rule.match):
                continue
            if tuple(normalized_base(token.text) for token in source) == rule.match:
                matched = rule
                matched_source = source
                break
        if matched is None:
            output.append(tokens[i])
            i += 1
            continue

        replacement_words = append_final_punctuation(list(matched.replacement), matched_source)
        timings = distribute_timing(matched_source, len(replacement_words))
        original = " ".join(token.text for token in matched_source)
        replacement = " ".join(replacement_words)
        for word, timing in zip(replacement_words, timings):
            output.append(
                CaptionToken(
                    text=word,
                    start=timing[0],
                    end=timing[1],
                    source_text=original,
                    flags=(matched.category, "virtual" if len(replacement_words) != len(matched_source) else "corrected"),
                )
            )
        decisions.append(
            CorrectionDecision(
                category=matched.category,
                original=original,
                replacement=replacement,
                reason=matched.reason,
                confidence=matched.confidence,
                span_start=i,
                span_end=i + len(matched.match),
            )
        )
        i += len(matched.match)
    return tuple(output), tuple(decisions)


def mark_spoken_acronyms(tokens: tuple[CaptionToken, ...]) -> tuple[tuple[CaptionToken, ...], tuple[CorrectionDecision, ...]]:
    output = list(tokens)
    decisions: list[CorrectionDecision] = []
    i = 0
    while i < len(output):
        run: list[int] = []
        j = i
        while j < len(output):
            base, punct = split_trailing_punctuation(output[j].text)
            if len(base) == 1 and base.isalpha():
                run.append(j)
                j += 1
                if punct:
                    break
                continue
            break
        acronym = "".join(split_trailing_punctuation(output[idx].text)[0] for idx in run).lower()
        if len(run) >= 2 and acronym in SPOKEN_ACRONYMS:
            original = " ".join(output[idx].text for idx in run)
            for idx in run:
                base, punct = split_trailing_punctuation(output[idx].text)
                flags = tuple(dict.fromkeys((*output[idx].flags, "spoken_acronym_letter", acronym)))
                output[idx] = replace(output[idx], text=f"{base.upper()}{punct}", flags=flags)
            decisions.append(
                CorrectionDecision(
                    category="spoken_acronym_timing",
                    original=original,
                    replacement=" ".join(output[idx].text for idx in run),
                    reason="The speaker spelled the acronym, so each letter should remain independently highlightable.",
                    confidence=0.99,
                    span_start=run[0],
                    span_end=run[-1] + 1,
                )
            )
            i = run[-1] + 1
        else:
            i += 1
    return tuple(output), tuple(decisions)


def apply_caption_policy(words: Sequence[str | CaptionToken]) -> PolicyResult:
    tokens = as_tokens(words)
    tokens, phrase_decisions = apply_phrase_rules(tokens)
    tokens, acronym_decisions = mark_spoken_acronyms(tokens)
    return PolicyResult(tokens=tokens, decisions=(*phrase_decisions, *acronym_decisions))


def normalize_text(text: str, uppercase: bool = False) -> str:
    result = apply_caption_policy(text.split())
    return result.caption_text(uppercase=uppercase)


def decisions_as_dicts(decisions: Iterable[CorrectionDecision]) -> list[dict[str, object]]:
    return [
        {
            "category": decision.category,
            "original": decision.original,
            "replacement": decision.replacement,
            "reason": decision.reason,
            "confidence": decision.confidence,
            "span_start": decision.span_start,
            "span_end": decision.span_end,
        }
        for decision in decisions
    ]


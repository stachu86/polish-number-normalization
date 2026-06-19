# This file is based on the English text normalizer from OpenAI Whisper:
# https://github.com/openai/whisper/blob/main/whisper/normalizers/english.py
#
# Original project: OpenAI Whisper
# Copyright (c) 2022 OpenAI
# Licensed under the MIT License.
#
# This implementation has been modified/adapted for Polish number normalization.

import json
import string
from decimal import *
import re
from fractions import Fraction
from pathlib import Path
from typing import Iterator, List, Match, Optional, Union
from more_itertools import windowed


class PolishNumberNormalizer:

    def __init__(self, ordinal_dot=False):
        super().__init__()
        data_dir = Path(__file__).resolve().parent / "data"
        self.ordinal_dot = ordinal_dot
        self.zeros = {"zero"}
        self.ones = {
            name: i
            for i, name in enumerate(
                [
                    "jeden",
                    "dwa",
                    "trzy",
                    "cztery",
                    "pięć",
                    "sześć",
                    "siedem",
                    "osiem",
                    "dziewięć",
                    "dziesięć",
                    "jedenaście",
                    "dwanaście",
                    "trzynaście",
                    "czternaście",
                    "piętnaście",
                    "szesnaście",
                    "siedemnaście",
                    "osiemnaście",
                    "dziewiętnaście",
                ],
                start=1,
            )
        }
        with (data_dir / "ordinals1.json").open("r", encoding="utf-8") as file:
            self.ones.update(json.load(file))

        self.tens = {
            "dwadzieścia": 20,
            "trzydzieści": 30,
            "czterdzieści": 40,
            "pięćdziesiąt": 50,
            "sześćdziesiąt": 60,
            "siedemdziesiąt": 70,
            "osiemdziesiąt": 80,
            "dziewięćdziesiąt": 90,
            "sto": 100,
            "dwieście": 200,
            "trzysta": 300,
            "czterysta": 400,
            "pięćset": 500,
            "sześćset": 600,
            "siedemset": 700,
            "osiemset": 800,
            "dziewięćset": 900,
            "tysiąc": 1000,
            "milion": 1000000,
            "miliard": 1000000000
        }

        with (data_dir / "ordinals2.json").open("r", encoding="utf-8") as file:
            self.tens.update(json.load(file))

        self.multipliers = {
            "dziesiąte": Decimal("0.1"),
            "dziesiąta": Decimal("0.1"),
            "dziesiątych": Decimal("0.1"),
            "setnych": Decimal("0.01"),
            "setne": Decimal("0.01"),
            "setna": Decimal("0.01"),
            "tysięcznych": Decimal("0.001"),
            "tysięczne": Decimal("0.001"),
            "tysięczna": Decimal("0.001"),

            "tysięcy": 1_000,
            "tysiące": 1_000,

            "milionów": 1_000_000,
            "miliony": 1_000_000,

            "miliardów": 1_000_000_000,
            "miliarda": 1_000_000_000,
        }

        self.decimals = {*self.ones, *self.tens, *self.zeros}

        self.preceding_prefixers = {
            "minus": "-",
            "plus": "+",
        }
        self.following_prefixers = {
            "funtów": "£",
            "funty": "£",
            "euro": "€",
            "dolrów": "$",
            "dolary": "$",
            "centy": "¢",
            "centów": "¢",
            "złotych": "zł",
            "złote": "zł",
            "groszy": "gr",
            "grosze": "gr",
        }
        self.prefixes = set(
            list(self.preceding_prefixers.values())
            + list(self.following_prefixers.values())
        )
        self.suffixers = {
            "procent": "%",
        }
        self.specials = {"i", "przecinek", "koma"}

        self.words = set(
            [
                key
                for mapping in [
                    self.zeros,
                    self.ones,
                    self.tens,
                    self.multipliers,
                    self.preceding_prefixers,
                    self.following_prefixers,
                    self.suffixers,
                    self.specials,
                ]
                for key in mapping
            ]
        )
        self.literal_words = {}

    def process_words(self, words: List[str]) -> Iterator[str]:
        prefix: Optional[str] = None
        value: Optional[Union[str, int]] = None
        skip = False
        time = False

        def to_fraction(s: str):
            try:
                return Fraction(s)
            except ValueError:
                return None

        def output(result: Union[str, int]):
            nonlocal prefix, value
            result = str(result)
            if prefix is not None:
                result = prefix + result
            value = None
            prefix = None
            return result

        if len(words) == 0:
            return

        for prev, current, next in windowed([None] + words + [None], 3):
            if skip:
                skip = False
                continue

            next_is_numeric = next is not None and re.match(
                r"^\d+(\.\d+)?$", next)
            has_prefix = current[0] in self.prefixes
            current_without_prefix = current[1:] if has_prefix else current
            if re.match(r"^\d+(\.\d+)?$", current_without_prefix):
                # arabic numbers (potentially with signs and fractions)
                f = to_fraction(current_without_prefix)
                assert f is not None
                if value is not None:
                    if isinstance(value, str) and value.endswith("."):
                        # concatenate decimals / ip address components
                        value = str(value) + str(current)
                        continue
                    else:
                        yield output(value)

                prefix = current[0] if has_prefix else prefix
                if f.denominator == 1:
                    value = f.numerator  # store integers as int
                else:
                    value = current_without_prefix
            elif current not in self.words:
                # non-numeric words
                if value is not None:
                    yield output(value)
                yield output(current)
            elif current in self.zeros:
                value = str(value or "") + "0"
            elif current in self.multipliers and value is not None:
                multiplier = self.multipliers[current]
                if isinstance(value, str) or value == 0:
                    f = to_fraction(value)
                    p = f * multiplier if f is not None else None
                    if f is not None and p.denominator == 1:
                        value = p.numerator
                    else:
                        yield output(value)
                        value = multiplier
                else:
                    before = value // 1000 * 1000
                    residual = value % 1000
                    value = before + residual * multiplier
            elif current in self.ones:
                ones = self.ones[current]

                if value is None:
                    if current[-1] in 'aj' and (1 <= ones <= 23) and current != "dwa": # possible time "godzina" druga, piętnasta, o szenstanstej...
                        time = True
                    value = ones
                elif isinstance(value, str) or prev in self.ones:
                    if (
                        prev in self.tens and ones < 10
                    ):  # replace the last zero with the digit
                        assert value[-1] == "0"
                        value = value[:-1] + str(ones)
                    elif isinstance(value, str) and ones < 100 and value[-2:] == "00":
                        value = value[:-2] + str(ones)
                    else:
                        if time:
                            if ones < 10:
                                ones = "0" + str(ones)
                            value = str(value) + ":" + str(ones)
                            time=False
                            continue
                        value = str(value) + str(ones)
                elif ones < 10:
                    if value % 10 == 0:
                        value += ones
                    else:
                        value = str(value) + str(ones)
                else:  # eleven to nineteen
                    if value % 100 == 0:
                        value += ones
                    else:
                        value = str(value) + str(ones)
            elif current in self.tens:
                tens = self.tens[current]
                if value is None:
                    value = tens
                elif isinstance(value, str):
                    value = str(value) + str(tens)
                else:
                    if value % 100 == 0:
                        value += tens
                    else:
                        if time:
                            value = str(value) + ":" + str(tens)
                            time=False
                            continue
                        value = str(value) + str(tens)
            elif current in self.preceding_prefixers:
                # apply prefix (positive, minus, etc.) if it precedes a number
                if value is not None:
                    yield output(value)

                if next in self.words or next_is_numeric:
                    prefix = self.preceding_prefixers[current]
                else:
                    yield output(current)
            elif current in self.following_prefixers:
                # apply prefix (dollars, cents, etc.) only after a number
                if value is not None:
                    prefix = self.following_prefixers[current]
                    yield output(value)
                else:
                    yield output(current)
            elif current in self.suffixers:
                # apply suffix symbols (percent -> '%')
                if value is not None:
                    suffix = self.suffixers[current]
                    if isinstance(suffix, dict):
                        if next in suffix:
                            yield output(str(value) + suffix[next])
                            skip = True
                        else:
                            yield output(value)
                            yield output(current)
                    else:
                        yield output(str(value) + suffix)
                else:
                    yield output(current)
            elif current in self.specials:
                if next not in self.words and not next_is_numeric:
                    # apply special handling only if the next word can be numeric
                    if value is not None:
                        yield output(value)
                    yield output(current)
                elif current == "i":
                    # ignore "and" after hundreds, thousands, etc.
                    if prev not in self.multipliers:
                        if value is not None:
                            yield output(value)
                        yield output(current)
                elif current == "double" or current == "triple":
                    if next in self.ones or next in self.zeros:
                        repeats = 2 if current == "double" else 3
                        ones = self.ones.get(next, 0)
                        value = str(value or "") + str(ones) * repeats
                        skip = True
                    else:
                        if value is not None:
                            yield output(value)
                        yield output(current)
                elif current == "przecinek" or current == "koma":
                    if next in self.decimals or next_is_numeric:
                        value = str(value or "") + ","
                elif current == "kropka":
                    if next in self.decimals or next_is_numeric:
                        value = str(value or "") + "<kropka>"
                else:
                    # should all have been covered at this point
                    raise ValueError(f"Unexpected token: {current}")
            else:
                # all should have been covered at this point
                raise ValueError(f"Unexpected token: {current}")

        if value is not None:
            yield output(value)

    def preprocess(self, s: str):
        # replace "<number> and a half" with "<number> point five"
        results = []
        s = s.lower()

        segments = re.split(r"\bi\s+pół\b", s)
        for i, segment in enumerate(segments):
            if len(segment.strip()) == 0:
                continue
            if i == len(segments) - 1:
                results.append(segment)
            else:
                results.append(segment)
                last_word = segment.rsplit(maxsplit=2)[-1]
                if last_word in self.decimals or last_word in self.multipliers:
                    results.append("przecinek pięć")
                else:
                    results.append("i pół")

        s = " ".join(results)

        # put a space at number/letter boundary
        s = re.sub(r"([a-z])([0-9])", r"\1 \2", s)
        s = re.sub(r"([0-9])([a-z])", r"\1 \2", s)

        # but remove spaces which could be a suffix
        s = re.sub(r"([0-9])\s+(st|nd|rd|th|s)\b", r"\1\2", s)

        # replace dot for comma in fractions
        s = re.sub(r'(\d)\.(\d)', r'\1,\2', s)

        # split punctuation with spaces
        punct = ''.join(ch for ch in string.punctuation if ch not in ",%")
        s = re.sub(
            rf"(?<!\d),(?!\d)|([{re.escape(punct)}])",
            r" \g<0> ",
            s
        )
        # s = re.sub(rf"([{re.escape(string.punctuation)}])", r" \1 ", s)
        return s

    def postprocess(self, s: str):
        def combine_cents(m: Match):
            try:
                currency = m.group(1)
                integer = m.group(2)
                cents = int(m.group(3))
                return f"{currency}{integer}.{cents:02d}"
            except ValueError:
                return m.string

        def extract_cents(m: Match):
            try:
                return f"¢{int(m.group(1))}"
            except ValueError:
                return m.string

        # apply currency postprocessing; "$2 and ¢7" -> "$2.07"
        s = re.sub(r"([€£$])([0-9]+) (?:and )?¢([0-9]{1,2})\b", combine_cents, s)
        s = re.sub(r"[€£$]0.([0-9]{1,2})\b", extract_cents, s)

        # replace dot for comma in fractions
        s = re.sub(r'(\d)\.(\d)', r'\1,\2', s)

        # join fractions conected by "i"
        s = re.sub(r'(\d) i 0\,(\d)', r'\1,\2', s)

        # remove extra spaces before punctations
        punct = ''.join(ch for ch in string.punctuation if ch not in "+-")
        s = re.sub(rf' ([{punct}])', r'\1', s)

        return s

    def __call__(self, s: str):
        s = self.preprocess(s)
        s = " ".join(word for word in self.process_words(s.split()) if word is not None)
        s = self.postprocess(s)

        return s



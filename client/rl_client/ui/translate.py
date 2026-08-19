from __future__ import annotations
from ..i18n import Translator


def get_translator(value=None) -> Translator:
    if isinstance(value, Translator):
        return value
    if isinstance(value, str):
        return Translator(value)
    return Translator("en")

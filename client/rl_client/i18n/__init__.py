from __future__ import annotations
from dataclasses import dataclass

from .keys import REQUIRED_KEYS
from .locales import LOCALES

SUPPORTED_LOCALES = {
    "en": "English",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español",
}


@dataclass
class Translator:
    locale: str = "en"

    def __post_init__(self) -> None:
        if self.locale not in LOCALES:
            self.locale = "en"

    def text(self, key: str, default: str | None = None, **values) -> str:
        raw = LOCALES[self.locale].get(key)
        if raw is None:
            raw = LOCALES["en"].get(key, default if default is not None else key)
        try:
            return raw.format(**values)
        except (KeyError, ValueError):
            return raw

    def has_native(self, key: str) -> bool:
        return key in LOCALES[self.locale]

    def language_name(self, locale: str | None = None) -> str:
        return SUPPORTED_LOCALES.get(locale or self.locale, locale or self.locale)

    __call__ = text


__all__ = ["Translator", "SUPPORTED_LOCALES", "REQUIRED_KEYS"]

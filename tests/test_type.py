import pytest
from mkdocs.config.base import ValidationError

from mkdocs_static_i18n.config import Locale


def test_locale_valid_values():
    locale = Locale(str)
    valid_locales = [
        "en",
        "en-US",
        "en_US",
        "fr",
        "fr-FR",
        "fr_FR",
        "ga",
        "sr-Latn",
        "th",
        "zh-Hans",
        "zh-Hans-CN",
        "zh-Hans-SG",
        "zh-Hant",
        "zh-Hant-HK",
        "zh-Hant-TW",
    ]
    for value in valid_locales:
        assert locale.run_validation(value) == value


def test_locale_invalid_values():
    locale = Locale(str)
    invalid_locales = [
        "english",
        "EN",
        "en-us",
        "123",
        "en-US-",
        "en_",
        "zh-Hans-sg",
    ]
    for value in invalid_locales:
        with pytest.raises(ValidationError):
            locale.run_validation(value)


def test_locale_null_value():
    locale = Locale(str)
    assert locale.run_validation("null") == "null"

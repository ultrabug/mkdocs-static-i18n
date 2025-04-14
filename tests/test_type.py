import pytest
from mkdocs.config.base import ValidationError

from mkdocs_static_i18n.config import Locale


def test_locale_valid_values():
    locale = Locale(str)
    valid_locales = [
        "en",
        "en-US",
        "en_US",
        "en-GB",
        "en-UK",  # valid pattern, but the territory code is not a valid ISO-3166-1 alpha-2 code
        "fr",
        "fr-FR",
        "fr_FR",
        "ga-IE",
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
        "123",  # language code must be two-letter ISO-639-1
        "english",  # language code must be two-letter ISO-639-1
        "EN",  # language code must be lower case
        "en-us",  # territory code must be upper case
        "en-US-",  # there must be no trailing dash
        "en_",  # there must be no trailing underscore
        "zh-Hans-sg",  # territory code must be upper case
    ]
    for value in invalid_locales:
        with pytest.raises(ValidationError):
            locale.run_validation(value)


def test_locale_null_value():
    locale = Locale(str)
    assert locale.run_validation("null") == "null"

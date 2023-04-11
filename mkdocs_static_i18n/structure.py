import logging
from re import compile

from mkdocs.config.base import ValidationError
from mkdocs.config.config_options import Type

RE_LOCALE = compile(r"(^[a-z]{2}(-[A-Za-z]{4})?(-[A-Z]{2})?$)|(^[a-z]{2}_[A-Z]{2}$)")

log = logging.getLogger("mkdocs.plugins." + __name__)


class Locale(Type):
    """
    Locale Config Option

    Validate the locale config option against a given Python type.
    """

    def _validate_locale(self, value):
        if not RE_LOCALE.match(value):
            raise ValidationError(
                "Language code values must be either ISO-639-1 lower case "
                "or represented with their territory/region/country codes, "
                f"received '{value}' expected forms examples: 'en' or 'en-US' or 'en_US'."
            )

    def _get_lang_dict_value(self, lang_key, lang_values):
        """
        languages:
          en:
            build: true
            default: true
            name: English
          fr:
            build: true
            name: Français
        """
        validate_types = {
            "build": bool,
            "default": bool,
            "fixed_link": str,
            "link": str,
            "name": str,
        }
        lang_config = {
            "default": False,
            "build": True,
            "link": f"./{lang_key}/",
            "fixed_link": None,
            "name": lang_key,
        }
        if isinstance(lang_values, dict):
            for key, value in lang_values.items():
                lang_config[key] = value
            for key, expected_type in validate_types.items():
                if type(lang_config.get(key)) not in [type(None), expected_type]:
                    raise ValidationError(
                        f"language config {key} unexpected type {type(lang_config.get(key))}"
                    )
            if lang_config["default"] is True:
                lang_config["link"] = "./"
        else:
            raise ValidationError("language config should be a dict")
        return lang_config

    def run_validation(self, value):
        value = super().run_validation(value)
        # languages
        if isinstance(value, dict):
            languages = {}
            default_count = 0
            for lang_key, lang_values in value.items():
                self._validate_locale(lang_key)
                languages[lang_key] = self._get_lang_dict_value(lang_key, lang_values)
                default_count += int(languages[lang_key]["default"])
            if default_count != 1:
                raise ValidationError(
                    "languages should contain one 'default: true' option"
                )
            value = languages
        else:
            raise ValidationError("languages should be a dict")
        return value

from re import compile

from mkdocs.config import config_options
from mkdocs.config.base import Config, ValidationError

RE_LOCALE = compile(r"(^[a-z]{2}(-[A-Za-z]{4})?(-[A-Z]{2})?$)|(^[a-z]{2}_[A-Z]{2}$)")


class Locale(config_options.Type):
    """
    Locale Config Option

    Validate the locale config option against a given Python type.
    """

    def run_validation(self, value):
        value = super().run_validation(value)
        if not RE_LOCALE.match(value) and value.lower() != "null":
            raise ValidationError(
                "Language code values must be either ISO-639-1 lower case "
                "or represented with their territory/region/country codes, "
                f"received '{value}' expected forms examples: 'en' or 'en-US' or 'en_US'."
            )
        return value


class I18nPluginLanguage(Config):
    """ """

    build = config_options.Type(bool, default=True)
    copyright = config_options.Optional(config_options.Type(str))
    default = config_options.Type(bool, default=False)
    extra = config_options.Optional(config_options.Type(dict))
    fixed_link = config_options.Optional(config_options.Type(str))
    link = config_options.Optional(config_options.Type(str))
    locale = Locale(str)
    name = config_options.Type(str)
    nav = config_options.Optional(config_options.Nav())
    nav_translations = config_options.Optional(config_options.Type(dict))
    admonition_translations = config_options.Optional(config_options.Type(dict))
    site_author = config_options.Optional(config_options.Type(str))
    site_description = config_options.Optional(config_options.Type(str))
    site_name = config_options.Optional(config_options.Type(str))
    site_url = config_options.Optional(config_options.Type(str))
    theme = config_options.Optional(config_options.Type(dict))

    def validate(self):
        failed, warnings = super().validate()
        # set defaults
        if self.link is None:
            if self.default:
                self.link = "/"
            else:
                self.link = f"/{self.locale}/"
        # link should be absolute and end with a trailing /
        else:
            if not self.link.startswith("/") or not self.link.endswith("/"):
                failed.append(
                    (
                        "link",
                        ValidationError(
                            f"languages[{self.locale}].link should be an absolute link starting "
                            f"with a leading / and ending with a / (like /{self.locale}/)."
                        ),
                    )
                )
        # special "null" locale can be used to insert an item in the language switcher
        # so it must never be built
        if self.locale == "null":
            self.build = False
            if self.fixed_link is None:
                failed.append(
                    (
                        "fixed_link",
                        ValidationError(
                            f"languages[{self.locale}].fixed_link should be set to a valid URL."
                        ),
                    )
                )
        return failed, warnings


class I18nPluginConfig(Config):
    """ """

    build_only_locale = config_options.Optional(Locale(str))
    docs_structure = config_options.Choice(["folder", "suffix"], default="suffix")
    fallback_to_default = config_options.Type(bool, default=True)
    reconfigure_material = config_options.Type(bool, default=True)
    reconfigure_search = config_options.Type(bool, default=True)
    languages = config_options.ListOfItems(
        config_options.SubConfig(I18nPluginLanguage, validate=True)
    )

    def validate(self):
        failed, warnings = super().validate()
        if not failed:
            if self.build_only_locale:
                # check that the build_only_locale is valid
                if self.build_only_locale not in [lang.locale for lang in self.languages]:
                    failed.append(
                        (
                            "build_only_locale",
                            ValidationError(
                                f"Locale {self.build_only_locale} is not present in languages"
                            ),
                        )
                    )
                # set other settings to valid values
                else:
                    for lang in self.languages:
                        is_the_only_lang = lang.locale == self.build_only_locale
                        lang.default = is_the_only_lang
                        lang.build = is_the_only_lang
            # check that we have at least a default language to build
            if not any(filter(lambda c: c.default and c.build, self.languages)):
                failed.append(
                    (
                        "languages",
                        ValidationError(
                            "Could not find a default language to build "
                            "(expecting 'default: true' AND 'build: true')."
                        ),
                    )
                )
        return failed, warnings

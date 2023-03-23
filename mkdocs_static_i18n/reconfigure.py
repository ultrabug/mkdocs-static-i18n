import logging
from pathlib import Path, PurePath
from urllib.parse import quote as urlquote

from mkdocs import localization
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.theme import Theme

from mkdocs_static_i18n import __file__ as installation_path

LUNR_LANGUAGES = [
    "ar",
    "da",
    "de",
    "en",
    "es",
    "fi",
    "fr",
    "hu",
    "it",
    "ja",
    "nl",
    "no",
    "pt",
    "ro",
    "ru",
    "sv",
    "th",
    "tr",
    "vi",
]
MKDOCS_THEMES = ["mkdocs", "readthedocs"]

log = logging.getLogger("mkdocs.plugins." + __name__)


def get_default_language(plugin_config: dict):
    for locale, lang_config in plugin_config["languages"].items():
        if lang_config["default"] is True:
            return locale


def get_languages_to_build(plugin_config: dict, all_languages):
    languages_to_build = []
    for locale in all_languages:
        lang_config = plugin_config["languages"][locale]
        if lang_config["build"] is True:
            languages_to_build.append(locale)
    return languages_to_build


def reconfigure_mkdocs_config(i18n_plugin, mkdocs_config: MkDocsConfig) -> MkDocsConfig:
    build_languages = i18n_plugin.build_languages
    i18n_config = mkdocs_config
    lang_config = i18n_plugin.config["languages"][i18n_plugin.current_language]
    locale = i18n_plugin.current_language
    plugin_config = i18n_plugin.config

    # MkDocs themes specific reconfiguration
    if mkdocs_config.theme.name in MKDOCS_THEMES:
        i18n_config.theme = reconfigure_mkdocs_theme(
            locale, i18n_config.theme, plugin_config
        )

    # material theme specific reconfiguration
    if mkdocs_config.theme.name == "material":
        i18n_config = reconfigure_material_theme(
            locale, i18n_config, plugin_config, build_languages
        )
        # warn about navigation.instant incompatibility
        if "navigation.instant" in mkdocs_config.theme._vars.get("features", []):
            log.warning(
                "mkdocs-material language switcher contextual link is not "
                "compatible with theme.features = navigation.instant"
            )

    # supported plugins reconfiguration
    for name, plugin in i18n_config.plugins.items():
        # search plugin (MkDocs & material > 9.0) reconfiguration
        if name in ["search", "material/search"]:
            i18n_config = reconfigure_search_plugin(
                i18n_config, plugin_config, build_languages, name, plugin
            )
        if name == "with-pdf":
            i18n_config = reconfigure_with_pdf_plugin(i18n_config)

    # apply localized user config overrides
    i18n_config = apply_user_overrides(i18n_config, lang_config)

    # Install a i18n aware version of sitemap.xml if not provided by the user
    if not Path(
        PurePath(i18n_config.theme._vars.get("custom_dir", "."))
        / PurePath("sitemap.xml")
    ).exists():
        custom_i18n_sitemap_dir = Path(
            PurePath(installation_path).parent / PurePath("custom_i18n_sitemap")
        ).resolve()
        i18n_config.theme.dirs.insert(0, str(custom_i18n_sitemap_dir))

    return i18n_config


def apply_user_overrides(i18n_config: MkDocsConfig, lang_config: dict):
    """
    The i18n configuration structure allows users to set abitrary configuration
    that will be overriden if they match valid MkDocsConfig or Theme options.
    """
    for lang_key, lang_override in lang_config.items():
        if lang_key in i18n_config.data and lang_override is not None:
            mkdocs_config_option_type = type(i18n_config.data[lang_key])
            # support special Theme object overrides
            if mkdocs_config_option_type == Theme and type(lang_override) == dict:
                i18n_config.theme = apply_user_theme_overrides(
                    i18n_config.theme, lang_override
                )
            elif mkdocs_config_option_type in [str, bool, dict, list]:
                i18n_config.load_dict({lang_key: lang_override})
    return i18n_config


def apply_user_theme_overrides(theme: Theme, options: dict) -> Theme:
    """
    Support and apply special mkdocs.Theme object overrides.
    """
    for key, value in options.items():
        if key in theme._vars and type(theme._vars[key]) == type(value):
            theme._vars[key] = value
        elif key == "locale":
            theme._vars[key] = localization.parse_locale(value)
        else:
            log.error(f"Failed to override unknown theme.{key}")
    return theme


def reconfigure_mkdocs_theme(locale: str, theme: Theme, plugin_config: dict) -> Theme:
    # set theme locale
    if "locale" in theme._vars:
        theme._vars["locale"] = localization.parse_locale(locale)
    return theme


def reconfigure_material_theme(
    locale: str, i18n_config: MkDocsConfig, plugin_config: dict, build_languages
) -> MkDocsConfig:
    # set theme language
    if "language" in i18n_config.theme._vars:
        i18n_config.theme._vars["language"] = locale
    # site language selector reconfiguration can be disabled
    if plugin_config["material_alternate"] is True:
        # configure extra.alternate language switcher
        if len(build_languages) > 1:
            # user has setup its own extra.alternate
            # warn him if it's poorly configured
            if "alternate" in i18n_config["extra"]:
                for alternate in i18n_config["extra"]["alternate"]:
                    if not alternate.get("link", "").startswith("./"):
                        log.info(
                            "The 'extra.alternate' configuration contains a "
                            "'link' option that should starts with './' in "
                            f"{alternate}"
                        )
            # configure the extra.alternate for the user
            else:
                i18n_config["extra"]["alternate"] = []
                # Add index.html file name when used with
                # use_directory_urls = True
                link_suffix = ""
                if i18n_config.get("use_directory_urls") is False:
                    link_suffix = "index.html"
                # setup language switcher
                for language in build_languages:
                    lang_config = plugin_config["languages"][language]
                    # skip language if not built
                    if lang_config["build"] is False:
                        continue
                    i18n_config["extra"]["alternate"].append(
                        {
                            "name": f"{lang_config['name']}",
                            "link": f"{lang_config['link']}{link_suffix}",
                            "fixed_link": lang_config["fixed_link"],
                            "lang": language,
                        }
                    )
    return i18n_config


def reconfigure_search_plugin(
    i18n_config: MkDocsConfig,
    plugin_config: dict,
    build_languages,
    search_plugin_name: str,
    search_plugin,
):
    # search plugin reconfiguration can be disabled
    if plugin_config["search_reconfigure"]:
        search_langs = search_plugin.config["lang"] or []
        for language in build_languages:
            if language in LUNR_LANGUAGES:
                if language not in search_langs:
                    search_langs.append(language)
                    log.info(
                        f"Adding '{language}' to the '{search_plugin_name}' plugin 'lang' option"
                    )
            else:
                log.warning(
                    f"Language '{language}' is not supported by "
                    f"lunr.js, not setting it in the 'plugins.search.lang' option"
                )
        if search_langs:
            search_plugin.config["lang"] = search_langs
    return i18n_config


def reconfigure_with_pdf_plugin(i18n_config):
    """
    Support plugin mkdocs-with-pdf, see #110.
    """
    if "with-pdf" in i18n_config["plugins"]:
        for events in i18n_config["plugins"].events.values():
            for idx, event in enumerate(list(events)):
                try:
                    if str(event.__module__) == "mkdocs_with_pdf.plugin":
                        events.pop(idx)
                except AttributeError:
                    # partials don't have a module
                    pass
    return i18n_config


def reconfigure_navigation(i18n_plugin, nav, mkdocs_config, i18n_files):
    """
    Apply static navigation items translation mapping for the current language.

    Localize the default homepage button.
    """
    # nav_translations
    nav_translations = i18n_plugin.config["languages"][
        i18n_plugin.current_language
    ].get("nav_translations", {})
    translated_items = 0
    for item in nav:
        if hasattr(item, "title") and item.title in nav_translations:
            item.title = nav_translations[item.title]
            translated_items += 1
        # is that the localized content homepage?
        if nav.homepage is None and hasattr(item, "url") and item.url:
            if item.url == f"{i18n_plugin.current_language}/":
                nav.homepage = item
    if translated_items:
        log.info(
            f"Translated {translated_items} navigation element"
            f"{'s' if translated_items > 1 else ''} to '{i18n_plugin.current_language}'"
        )
    # report missing homepage
    if nav.homepage is None:
        log.warning(
            f"Could not find a homepage for locale '{i18n_plugin.current_language}'"
        )
    return nav


def reconfigure_markdown(i18n_plugin, page):
    """
    Apply translation mapping for the current language to the given page
    and its children.

    TODO: dead code, obsolete?
    """
    nav_translations = i18n_plugin.config["languages"][
        i18n_plugin.current_language
    ].get("nav_translations", {})
    if hasattr(page, "title") and page.title in nav_translations:
        page.title = nav_translations[page.title]
        log.info(f"Translated page title to '{i18n_plugin.current_language}'")
    if hasattr(page, "children") and page.children:
        for child in page.children:
            reconfigure_markdown(i18n_plugin, child)
    return page


def reconfigure_page_context(i18n_plugin, context, page, i18n_config, nav):
    """
    Support dynamic reconfiguration of the material language selector so that
    users can switch between the different localized versions of their current page.
    """
    # TODO: switch to using page.alternates to avoid 404 on missing content?
    # site language selector reconfiguration can be disabled
    if i18n_plugin.config["material_alternate"] is True:
        if PurePath(page.url) == PurePath("."):
            return context
        alternates = []
        for current_alternate in i18n_config["extra"]["alternate"]:
            new_alternate = {}
            new_alternate.update(**current_alternate)
            # page is part of the localized language path
            if PurePath(page.url).is_relative_to(i18n_plugin.current_language):
                # link to the default root path should not prefix the locale
                if current_alternate["lang"] == i18n_plugin.default_language:
                    new_alternate["link"] = urlquote(
                        PurePath(page.url)
                        .relative_to(i18n_plugin.current_language)
                        .as_posix()
                    )
                # link to other locales should prefix the locale
                else:
                    # there is an alternate page for this page, link to it
                    if current_alternate["lang"] in page.file.alternates:
                        new_alternate["link"] = urlquote(
                            PurePath(
                                PurePath(current_alternate["lang"])
                                / PurePath(page.url).relative_to(
                                    i18n_plugin.current_language
                                )
                            ).as_posix()
                        )
                    # there is no alternate page for this page, link to root
                    else:
                        new_alternate["link"] = urlquote(
                            PurePath(current_alternate["lang"]).as_posix()
                        )

            # page is part of the default language root path
            else:
                if current_alternate["lang"] == i18n_plugin.current_language:
                    new_alternate["link"] = page.url
                else:
                    new_alternate["link"] = urlquote(
                        PurePath(
                            PurePath(current_alternate["lang"]) / PurePath(page.url)
                        ).as_posix()
                    )
            new_alternate["link"] = f"./{new_alternate['link']}"
            alternates.append(new_alternate)
        context["config"]["extra"]["alternate"] = alternates
    return context


def reconfigure_alternates(self):
    """
    Reconfigure File() alternates of all languages built so far.
    """
    for build_locale, build_dest_uris in self.i18n_dest_uris.items():
        for i18n_file in build_dest_uris.values():
            alternates = {}
            for expected_language in self.build_languages:
                if build_locale == self.default_language:
                    if expected_language == self.default_language:
                        expected_dest_uri = PurePath(i18n_file.dest_uri).as_posix()
                    else:
                        expected_dest_uri = PurePath(
                            PurePath(expected_language) / i18n_file.dest_uri
                        ).as_posix()
                else:
                    if expected_language == self.default_language:
                        expected_dest_uri = PurePath(
                            PurePath(i18n_file.dest_uri).relative_to(build_locale)
                        ).as_posix()
                    else:
                        expected_dest_uri = PurePath(
                            PurePath(expected_language)
                            / PurePath(i18n_file.dest_uri).relative_to(build_locale)
                        ).as_posix()
                # lookup the expected language alternate i18n_file, if present
                if expected_language in self.i18n_dest_uris:
                    if expected_dest_uri in self.i18n_dest_uris[expected_language]:
                        alternates[expected_language] = self.i18n_dest_uris[
                            expected_language
                        ][expected_dest_uri]
            i18n_file.alternates = alternates
    return self.i18n_alternates

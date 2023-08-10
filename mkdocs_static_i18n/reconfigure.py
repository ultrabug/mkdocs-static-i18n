from copy import deepcopy
from pathlib import Path, PurePath
from urllib.parse import urlsplit

from mkdocs import localization
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page
from mkdocs.theme import Theme

from mkdocs_static_i18n import __file__ as installation_path
from mkdocs_static_i18n.config import I18nPluginConfig
from mkdocs_static_i18n.suffix import I18nFiles

log = get_plugin_logger(__name__)

try:
    from importlib.metadata import files as package_files

    LUNR_LANGUAGES = [
        PurePath(lang.stem).suffix.replace(".", "")
        for lang in package_files("mkdocs")
        if "mkdocs/contrib/search/lunr-language/lunr." in lang.as_posix() and len(lang.stem) == 7
    ]
    assert len(LUNR_LANGUAGES) > 1
    LUNR_LANGUAGES.append("en")
except Exception:
    LUNR_LANGUAGES = [
        "ar",
        "da",
        "de",
        "du",
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
    log.warning("Unable to detect lunr languages from mkdocs distribution")
MKDOCS_THEMES = ["mkdocs", "readthedocs"]


class ExtendedPlugin(BasePlugin[I18nPluginConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.building = False
        self.current_language = None
        self.extra_alternate = {}
        self.i18n_alternates = {}
        self.search_entries = []
        self.original_configs = {}
        self.original_theme_configs = {}

    @property
    def all_languages(self):
        return [lang.locale for lang in self.config.languages]

    @property
    def default_language(self):
        for lang_config in self.config.languages:
            if lang_config.default is True:
                return lang_config.locale

    @property
    def current_language_config(self):
        return self.get_language_config(self.current_language)

    @property
    def is_default_language_build(self):
        return self.current_language == self.default_language

    @property
    def build_languages(self):
        return [
            lang.locale for lang in filter(lambda lang: lang.build is True, self.config.languages)
        ]

    def get_language_config(self, locale):
        for lang_config in filter(lambda lang: lang.locale == locale, self.config.languages):
            return lang_config
        raise Exception(f"Could not find language locale '{locale}'")

    def reconfigure_mkdocs_config(self, config: MkDocsConfig) -> MkDocsConfig:
        # MkDocs themes specific reconfiguration
        if config.theme.name in MKDOCS_THEMES:
            self.reconfigure_mkdocs_theme(config, self.current_language)

        # material theme specific reconfiguration (can be disabled)
        if config.theme.name == "material" and self.config["reconfigure_material"] is True:
            config = self.reconfigure_material_theme(config, self.current_language)
            # warn about navigation.instant incompatibility
            if "navigation.instant" in config.theme._vars.get("features", []):
                log.warning(
                    "mkdocs-material language switcher contextual link is not "
                    "compatible with theme.features = navigation.instant"
                )

        # supported plugins reconfiguration
        for name, plugin in config.plugins.items():
            # search plugin (MkDocs & material > 9.0) reconfiguration
            if name in ["search", "material/search"]:
                # search plugin reconfiguration can be disabled
                if self.config["reconfigure_search"]:
                    config = self.reconfigure_search_plugin(config, name, plugin)
            if name == "with-pdf":
                config = self.reconfigure_with_pdf_plugin(config)

        # apply localized user config overrides
        config = self.apply_user_overrides(config)

        # Install a i18n aware version of sitemap.xml if not provided by the user
        if not Path(
            PurePath(config.theme._vars.get("custom_dir", ".")) / PurePath("sitemap.xml")
        ).exists():
            custom_i18n_sitemap_dir = Path(
                PurePath(installation_path).parent / PurePath("custom_i18n_sitemap")
            ).resolve()
            config.theme.dirs.insert(0, str(custom_i18n_sitemap_dir))

        return config

    def reset_to_original_config(self, config: MkDocsConfig):
        """
        Since applying user overrides on each language build is done
        on the same MkDocs config instance, we need to reset parts of
        it before overriding it again.

        Example:
            - the general config has a default site_name defined
            - we build for "en", "fr", "de" (in that order)
            - if site_name is overridden for "fr" but NOT for "de"
            - then "de" would get the "fr" site_name instead of the general one

        This method takes care of that problem.
        """
        for config_key, config_value in self.original_configs.items():
            config[config_key] = config_value
        for config_key, config_value in self.original_theme_configs.items():
            config.theme._vars[config_key] = config_value

        return config

    def save_original_config(self, store, key, value):
        if key not in store:
            store[key] = value

    def apply_user_overrides(self, config: MkDocsConfig):
        """
        The i18n configuration structure allows users to set abitrary configuration
        that will be overriden if they match valid MkDocsConfig or Theme options.
        """
        # reset config to its orginal values since the config might have been
        # altered by a previous build
        config = self.reset_to_original_config(config)

        for lang_key, lang_override in self.current_language_config.items():
            if lang_key in config.data and lang_override is not None:
                mkdocs_config_option_type = type(config.data[lang_key])
                # support special Theme object overrides
                if mkdocs_config_option_type == Theme and type(lang_override) == dict:
                    config.theme = self.apply_user_theme_overrides(config.theme, lang_override)
                elif mkdocs_config_option_type in [str, bool, dict, list]:
                    self.save_original_config(
                        self.original_configs, lang_key, config.data[lang_key]
                    )
                    config.load_dict({lang_key: lang_override})
        return config

    def apply_user_theme_overrides(self, theme: Theme, options: dict) -> Theme:
        """
        Support and apply special mkdocs.Theme object overrides.
        """
        for key, value in options.items():
            if key in theme._vars and type(theme._vars[key]) == type(value):
                self.save_original_config(self.original_theme_configs, key, theme._vars[key])
                theme._vars[key] = value
            elif key == "locale":
                self.save_original_config(self.original_theme_configs, key, theme._vars[key])
                theme._vars[key] = localization.parse_locale(value)
            else:
                log.error(f"Failed to override unknown theme.{key}")
        return theme

    def reconfigure_mkdocs_theme(self, config: MkDocsConfig, locale: str) -> Theme:
        # set theme locale
        if "locale" in config.theme._vars:
            config.theme._vars["locale"] = localization.parse_locale(locale)

    def reconfigure_material_theme(self, config: MkDocsConfig, locale: str) -> MkDocsConfig:
        # set theme language
        if "language" in config.theme._vars:
            config.theme._vars["language"] = locale
        # configure extra.alternate language switcher
        if len(self.build_languages) > 1:
            # 'on_page_context' overrides the config.extra.alternate
            # so we need to reset it to its initial computed value if present
            if self.extra_alternate:
                config["extra"]["alternate"] = deepcopy(self.extra_alternate)
            # user has setup its own extra.alternate
            # warn if it's poorly configured
            if "alternate" in config["extra"]:
                for alternate in config["extra"]["alternate"]:
                    if not alternate.get("link", "").startswith("/") or not alternate.get(
                        "link", ""
                    ).endswith("/"):
                        log.info(
                            "The 'extra.alternate' configuration contains a "
                            "'link' option that should be an absolute path '/' and "
                            f"end with a trailing '/' in {alternate}"
                        )
                    for required_key in ["name", "link", "lang"]:
                        if required_key not in alternate:
                            log.info(
                                "The 'extra.alternate' configuration is missing a required "
                                f"'{required_key}' option in {alternate}"
                            )
            # configure the extra.alternate for the user
            # https://squidfunk.github.io/mkdocs-material/setup/changing-the-language/#site-language-selector
            else:
                base_url = urlsplit(config.site_url).path.rstrip("/")
                config["extra"]["alternate"] = []
                # Add index.html file name when used with
                # use_directory_urls = True
                link_suffix = "" if config.get("use_directory_urls") else "index.html"
                # setup language switcher
                for language in self.build_languages:
                    lang_config = self.get_language_config(language)
                    # skip language if not built
                    if lang_config.build is False:
                        continue
                    config["extra"]["alternate"].append(
                        {
                            "name": lang_config.name,
                            "link": lang_config.fixed_link
                            or f"{base_url}{lang_config.link}{link_suffix}",
                            "lang": language,
                        }
                    )
            self.extra_alternate = deepcopy(config["extra"]["alternate"])
        return config

    def reconfigure_search_plugin(
        self, config: MkDocsConfig, search_plugin_name: str, search_plugin
    ):
        search_langs = search_plugin.config["lang"] or []
        for language in self.build_languages:
            if language in LUNR_LANGUAGES:
                if language not in search_langs:
                    search_langs.append(language)
                    log.info(
                        f"Adding '{language}' to the '{search_plugin_name}' plugin 'lang' option"
                    )
            else:
                log.info(
                    f"Language '{language}' is not supported by "
                    f"lunr.js, not setting it in the 'plugins.search.lang' option"
                )
        if search_langs:
            search_plugin.config["lang"] = search_langs
        return config

    def reconfigure_with_pdf_plugin(self, config: MkDocsConfig):
        """
        Support plugin mkdocs-with-pdf, see #110.
        """
        for events in config["plugins"].events.values():
            for idx, event in enumerate(list(events)):
                try:
                    if str(event.__module__) == "mkdocs_with_pdf.plugin":
                        events.pop(idx)
                except AttributeError:
                    # partials don't have a module
                    pass
        return config

    def reconfigure_navigation(
        self, nav: Navigation, config: MkDocsConfig, files: I18nFiles, nav_helper
    ):
        """
        Apply static navigation items translation mapping for the current language.

        Localize the default homepage button.
        """
        # nav_translations
        nav_translations = self.current_language_config.nav_translations or {}

        for item in nav:
            if hasattr(item, "title") and item.title in nav_translations:
                item.title = nav_translations[item.title]
                nav_helper.translated_items += 1

            # is that the localized content homepage?
            if nav_helper.homepage is None and isinstance(item, Page):
                if item.url in nav_helper.expected_homepage_urls or item.url == "":
                    nav_helper.homepage = item

            # translation should be recursive to children
            if hasattr(item, "children") and item.children:
                self.reconfigure_navigation(item.children, config, files, nav_helper)

        return nav

    def reconfigure_page_context(self, context, page, config: MkDocsConfig, nav: Navigation):
        """
        Support dynamic reconfiguration of the material language selector so that
        users can switch between the different localized versions of their current page.
        """
        if self.extra_alternate:
            config["extra"]["alternate"] = deepcopy(self.extra_alternate)
            if PurePath(page.url) == PurePath("."):
                return context
            if PurePath(page.url) == PurePath(page.file.locale_alternate_of):
                return context
            #
            for extra_alternate in config["extra"]["alternate"]:
                alternate_lang = extra_alternate["lang"]
                # current page has an alternate for this language, use it
                if alternate_lang in page.file.alternates:
                    alternate_file = page.file.alternates[alternate_lang]
                    extra_alternate["link"] = alternate_file.url
        return context

    def extend_search_entries(self, config: MkDocsConfig):
        """
        Stack up search plugin entries as we build languages one after the other
        and deduplicate entries at the same time.
        """
        for name, plugin in config.plugins.items():
            if name in ["search", "material/search"]:
                if hasattr(plugin, "search_index"):
                    entries = getattr(plugin.search_index, "entries", None) or getattr(
                        plugin.search_index, "_entries"
                    )
                    self.search_entries.extend(entries)

    def reconfigure_search_duplicates(self, search_index_entries):
        """
        We want to avoid indexing the same pages twice if the default language
        has its own version built as well as the /language version too as this
        would pollute the search results.
        When this happens, we favor the default language location if its
        content is the same as its /language counterpart.
        """
        default_lang_entries = filter(
            lambda x: not x["location"].startswith(
                tuple([f"{lang}/" for lang in self.build_languages])
            ),
            search_index_entries,
        )
        target_lang_entries = list(
            filter(
                lambda x: x["location"].startswith(
                    tuple([f"{lang}/" for lang in self.build_languages])
                ),
                search_index_entries,
            )
        )
        for default_lang_entry in default_lang_entries:
            duplicated_entries = filter(
                lambda x: x["title"] == default_lang_entry["title"]
                and x["location"].endswith(x["location"])
                and x["text"] == default_lang_entry["text"],
                target_lang_entries,
            )
            for duplicated_entry in duplicated_entries:
                if duplicated_entry in search_index_entries:
                    log.debug(
                        f"removed duplicated search entry: {duplicated_entry['title']} "
                        f"{duplicated_entry['location']}"
                    )
                    search_index_entries.remove(duplicated_entry)

    def reconfigure_search_index(self, config: MkDocsConfig):
        """
        Stack up search plugin entries as we build languages one after the other
        and deduplicate entries at the same time.
        """
        for name, plugin in config.plugins.items():
            if name in ["search", "material/search"]:
                attribute_name = (
                    "_entries" if hasattr(plugin.search_index, "_entries") else "entries"
                )
                try:
                    search_index_entries = getattr(plugin.search_index, attribute_name)
                except AttributeError:
                    log.warning(
                        f"Can't access the search index entries in {name} ({attribute_name})."
                    )
                    return
                # clear and repopulate the search index
                search_index_entries.clear()
                search_index_entries.extend(self.search_entries)
                # remove search index duplicates
                if self.config["reconfigure_search"]:
                    self.reconfigure_search_duplicates(search_index_entries)
                # run the post_build event to rebuild the search index
                plugin.on_post_build(config=config)

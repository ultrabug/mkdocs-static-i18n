import logging
from pathlib import Path, PurePath
from urllib.parse import quote as urlquote

from mkdocs import localization
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page
from mkdocs.theme import Theme

from mkdocs_static_i18n import __file__ as installation_path
from mkdocs_static_i18n import is_relative_to
from mkdocs_static_i18n.config import I18nPluginConfig
from mkdocs_static_i18n.suffix import I18nFiles

log = logging.getLogger("mkdocs.plugins." + __name__)

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
        self.i18n_alternates = {}
        self.i18n_dest_uris = {}
        self.search_entries = []

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

    def apply_user_overrides(self, config: MkDocsConfig):
        """
        The i18n configuration structure allows users to set abitrary configuration
        that will be overriden if they match valid MkDocsConfig or Theme options.
        """
        for lang_key, lang_override in self.current_language_config.items():
            if lang_key in config.data and lang_override is not None:
                mkdocs_config_option_type = type(config.data[lang_key])
                # support special Theme object overrides
                if mkdocs_config_option_type == Theme and type(lang_override) == dict:
                    config.theme = self.apply_user_theme_overrides(config.theme, lang_override)
                elif mkdocs_config_option_type in [str, bool, dict, list]:
                    config.load_dict({lang_key: lang_override})
        return config

    def apply_user_theme_overrides(self, theme: Theme, options: dict) -> Theme:
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
            # user has setup its own extra.alternate
            # warn him if it's poorly configured
            if "alternate" in config["extra"]:
                for alternate in config["extra"]["alternate"]:
                    if not alternate.get("link", "").startswith("./"):
                        log.info(
                            "The 'extra.alternate' configuration contains a "
                            "'link' option that should starts with './' in "
                            f"{alternate}"
                        )
            # configure the extra.alternate for the user
            else:
                config["extra"]["alternate"] = []
                # Add index.html file name when used with
                # use_directory_urls = True
                link_suffix = ""
                if config.get("use_directory_urls") is False:
                    link_suffix = "index.html"
                # setup language switcher
                for language in self.build_languages:
                    lang_config = self.get_language_config(language)
                    # skip language if not built
                    if lang_config.build is False:
                        continue
                    config["extra"]["alternate"].append(
                        {
                            "name": f"{lang_config['name']}",
                            "link": f"{lang_config['link']}{link_suffix}",
                            "fixed_link": lang_config["fixed_link"],
                            "lang": language,
                        }
                    )
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
        # TODO: switch to using page.alternates to avoid 404 on missing content?
        if PurePath(page.url) == PurePath("."):
            return context
        alternates = []
        for current_alternate in config["extra"].get("alternate", {}):
            new_alternate = {}
            new_alternate.update(**current_alternate)
            # page is part of the localized language path
            if is_relative_to(page.url, self.current_language):
                # link to the default root path should not prefix the locale
                if current_alternate["lang"] == self.default_language:
                    new_alternate["link"] = urlquote(
                        PurePath(page.url).relative_to(self.current_language).as_posix()
                    )
                # link to other locales should prefix the locale
                else:
                    # there is an alternate page for this page, link to it
                    if current_alternate["lang"] in page.file.alternates:
                        new_alternate["link"] = urlquote(
                            PurePath(
                                PurePath(current_alternate["lang"])
                                / PurePath(page.url).relative_to(self.current_language)
                            ).as_posix()
                        )
                    # there is no alternate page for this page, link to root
                    else:
                        new_alternate["link"] = urlquote(
                            PurePath(current_alternate["lang"]).as_posix()
                        )

            # page is part of the default language root path
            else:
                if current_alternate["lang"] == self.current_language:
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

    def reconfigure_alternates(self, i18n_files):
        """
        Reconfigure File() alternates of all languages built so far.
        """
        # because we build one language after the other, we need to rebuild
        # the alternates for each of them until the last built language
        # keep a reference of the i18n_files to build the alterntes for
        self.i18n_alternates[self.current_language] = i18n_files
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
                            alternates[expected_language] = self.i18n_dest_uris[expected_language][
                                expected_dest_uri
                            ]
                i18n_file.alternates = alternates
        return self.i18n_alternates

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

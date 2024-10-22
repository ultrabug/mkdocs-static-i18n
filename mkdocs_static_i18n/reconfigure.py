from collections import defaultdict
from copy import deepcopy
from pathlib import Path, PurePath
from typing import Union
from urllib.parse import urlsplit

from mkdocs import localization
from mkdocs.config.base import LegacyConfig
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.files import File, Files
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page
from mkdocs.theme import Theme

from mkdocs_static_i18n import __file__ as installation_path
from mkdocs_static_i18n import folder, is_relative_to, suffix
from mkdocs_static_i18n.config import I18nPluginConfig

log = get_plugin_logger(__name__)

try:
    from importlib.metadata import version

    MATERIAL_VERSION = version("mkdocs-material")
except Exception:
    try:
        # python 3.7 compatibility, drop on 3.7 EOL
        import pkg_resources

        MATERIAL_VERSION = pkg_resources.get_distribution("mkdocs-material").version
    except Exception:
        MATERIAL_VERSION = None

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
        "hi",
        "hu",
        "hy",
        "it",
        "ja",
        "jp",
        "kn",
        "ko",
        "nl",
        "no",
        "pt",
        "ro",
        "ru",
        "sa",
        "sv",
        "ta",
        "te",
        "th",
        "tr",
        "vi",
        "zh",
    ]
    log.warning("Unable to detect lunr languages from mkdocs distribution")
MKDOCS_THEMES = ["mkdocs", "readthedocs"]


class ExtendedPlugin(BasePlugin[I18nPluginConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.building = False
        self.current_language = None
        self.extra_alternate = {}
        self.i18n_files_per_language = {}
        self.original_configs = {}
        self.original_theme_configs = {}
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
        if config.theme.name == "material" and self.config.reconfigure_material is True:
            # check and warn about missing mkdocs-material version
            if MATERIAL_VERSION is None:
                log.warning("mkdocs-material version could not be detected")
            elif MATERIAL_VERSION <= "7.1":
                log.warning(f"mkdocs-material version {MATERIAL_VERSION} is not supported")
            else:
                config = self.reconfigure_material_theme(config, self.current_language)
                # warn about navigation.instant incompatibility
                if "navigation.instant" in config.theme.get("features", []):
                    log.warning(
                        "mkdocs-material language switcher contextual link is not "
                        "compatible with theme.features = navigation.instant"
                    )

        # supported plugins reconfiguration
        for name, plugin in config.plugins.items():
            # search plugin (MkDocs & material > 9.0) reconfiguration
            if name in ["search", "material/search"]:
                # search plugin reconfiguration can be disabled
                if self.config.reconfigure_search:
                    config = self.reconfigure_search_plugin(config, name, plugin)
            if name == "with-pdf":
                config = self.reconfigure_with_pdf_plugin(config)

        # apply localized user config overrides
        config = self.apply_user_overrides(config)

        # Install a i18n aware version of sitemap.xml if not provided by the user
        if not Path(
            PurePath(config.theme.get("custom_dir", ".")) / PurePath("sitemap.xml")
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
            config.theme[config_key] = config_value

        return config

    def save_original_config(self, store, key, value):
        if key not in store:
            store[key] = deepcopy(value)

    def apply_user_overrides(self, config: MkDocsConfig):
        """
        The i18n configuration structure allows users to set abitrary configuration
        that will be overriden if they match valid MkDocsConfig or Theme options.
        """
        # reset config to its orginal values since the config might have been
        # altered by a previous build
        config = self.reset_to_original_config(config)

        # some config overrides are forbidden as they make no sense
        forbidden_config_overrides = [
            "dev_addr",
            "docs_dir",
            "edit_uri_template",
            "edit_uri",
            "exclude_docs",
            "extra_css",
            "extra_javascript",
            "extra_templates",
            "hooks",
            "markdown_extensions",
            "mdx_configs",
            "not_in_nav",
            "plugins",
            "remote_branch",
            "remote_name",
            "repo_name",
            "repo_url",
            "site_dir",
            "strict",
            "use_directory_urls",
            "validation",
            "watch",
        ]
        for lang_key, lang_override in self.current_language_config.items():
            if lang_key in forbidden_config_overrides:
                log.warning(
                    f"Ignoring forbidden '{self.current_language}' config override '{lang_key}'"
                )
                continue
            if lang_key in config.data and lang_override is not None:
                mkdocs_config_option_type = type(config.data[lang_key])
                # support special Theme object overrides
                if mkdocs_config_option_type == Theme and isinstance(lang_override, dict):
                    config.theme = self.apply_user_theme_overrides(config.theme, lang_override)
                elif mkdocs_config_option_type in [str, bool, dict, list, type(None)]:
                    self.save_original_config(
                        self.original_configs, lang_key, config.data[lang_key]
                    )
                    config.load_dict({lang_key: lang_override})
                    log.info(
                        f"Overriding '{self.current_language}' config '{lang_key}' with '{lang_override}'"
                    )
                # extra is a legacy dict config
                elif mkdocs_config_option_type == LegacyConfig:
                    self.save_original_config(
                        self.original_configs, lang_key, config.data[lang_key]
                    )
                    config[lang_key].update(lang_override)
                    log.info(
                        f"Updating '{self.current_language}' config '{lang_key}' with '{lang_override}'"
                    )
                else:
                    log.warning(f"Unknown '{self.current_language}' config override '{lang_key}'")
        return config

    def apply_user_theme_overrides(self, theme: Theme, options: dict) -> Theme:
        """
        Support and apply special mkdocs.Theme object overrides.
        """

        def dict_recursive_update(source, overrides):
            for key, value in overrides.items():
                if isinstance(value, dict) and value:
                    updated = dict_recursive_update(source.get(key, {}), value)
                    source[key] = updated
                else:
                    source[key] = overrides[key]
            return source

        for key, value in options.items():
            if key in theme and type(theme[key]) is type(value):
                self.save_original_config(self.original_theme_configs, key, theme[key])
                log.info(
                    f"Overriding '{self.current_language}' config 'theme.{key}' with '{value}'"
                )
                if isinstance(value, dict):
                    dict_recursive_update(theme[key], value)
                elif isinstance(value, list):
                    for idx, item in enumerate(value):
                        if isinstance(item, dict):
                            dict_recursive_update(theme[key][idx], item)
                        else:
                            theme[key][idx] = item
                else:
                    theme[key] = value
            elif key == "locale":
                self.save_original_config(self.original_theme_configs, key, theme[key])
                theme[key] = localization.parse_locale(value)
                log.info(
                    f"Overriding '{self.current_language}' config 'theme.{key}' with '{value}'"
                )
            else:
                log.warning(f"Unknown '{self.current_language}' config override 'theme.{key}'")
        return theme

    def reconfigure_mkdocs_theme(self, config: MkDocsConfig, locale: str) -> Theme:
        # set theme locale
        if "locale" in config.theme:
            config.theme["locale"] = localization.parse_locale(locale)

    def reconfigure_material_theme(self, config: MkDocsConfig, locale: str) -> MkDocsConfig:
        # set theme language
        if "language" in config.theme:
            config.theme["language"] = locale
        # configure extra.alternate language switcher
        if len(self.build_languages) > 1 or "null" in self.all_languages:
            # 'on_page_context' overrides the config.extra.alternate
            # so we need to reset it to its initial computed value if present
            if self.extra_alternate:
                config.extra["alternate"] = deepcopy(self.extra_alternate)
            # user has setup its own extra.alternate
            # warn if it's poorly configured
            if "alternate" in config.extra:
                for alternate in config.extra["alternate"]:
                    alternate_link = alternate.get("link", "")
                    if not alternate_link.startswith("http") and (
                        not alternate_link.startswith("/") or not alternate_link.endswith("/")
                    ):
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
                if config.site_url:
                    base_url = urlsplit(config.site_url).path.rstrip("/")
                else:
                    base_url = ""
                config.extra["alternate"] = []
                # Add index.html file name when used with
                # use_directory_urls = True
                link_suffix = "" if config.get("use_directory_urls") else "index.html"
                # setup language switcher
                for language in self.all_languages:
                    lang_config = self.get_language_config(language)
                    # skip language if not built unless we are the special "null" locale
                    if lang_config.build is False and lang_config.locale != "null":
                        continue
                    config.extra["alternate"].append(
                        {
                            "name": lang_config.name,
                            "link": lang_config.fixed_link
                            or f"{base_url}{lang_config.link}{link_suffix}",
                            "lang": language,
                        }
                    )
            self.extra_alternate = deepcopy(config.extra["alternate"])
        return config

    def reconfigure_search_plugin(
        self, config: MkDocsConfig, search_plugin_name: str, search_plugin
    ):
        search_langs = search_plugin.config.lang or []
        for language in self.build_languages:
            if language in LUNR_LANGUAGES:
                if language not in search_langs:
                    search_langs.append(language)
                    log.info(
                        f"Adding '{language}' to the '{search_plugin_name}' plugin 'lang' option"
                    )
            elif language == self.current_language:
                log.info(
                    f"Language '{language}' is not supported by "
                    f"lunr.js, not setting it in the 'plugins.search.lang' option"
                )
        if search_langs:
            search_plugin.config.lang = search_langs
        return config

    def reconfigure_with_pdf_plugin(self, config: MkDocsConfig):
        """
        Support plugin mkdocs-with-pdf, see #110.
        """
        for events in config.plugins.events.values():
            for idx, event in enumerate(list(events)):
                try:
                    if str(event.__module__) == "mkdocs_with_pdf.plugin":
                        events.pop(idx)
                except AttributeError:
                    # partials don't have a module
                    pass
        return config

    def reconfigure_navigation(
        self,
        nav: Navigation,
        config: MkDocsConfig,
        files: Union[suffix.I18nFiles, folder.I18nFiles],
        nav_helper,
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
            config.extra.alternate = deepcopy(self.extra_alternate)
            if PurePath(page.url) == PurePath("."):
                return context
            if PurePath(page.url) == PurePath(page.file.locale_alternate_of):
                return context
            #
            for extra_alternate in config.extra.alternate:
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
                    for entries_attr in ["entries", "_entries"]:
                        if hasattr(plugin.search_index, entries_attr):
                            entries = getattr(plugin.search_index, entries_attr)
                            self.search_entries.extend(entries)
                            break
                    else:
                        log.warning(f"Could not find '{name}' plugin search entries")

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
                and x["location"].endswith(default_lang_entry["location"])
                and x["text"] == default_lang_entry["text"],
                target_lang_entries,
            )
            for duplicated_entry in duplicated_entries:
                log.debug(
                    f"removed duplicated search entry: {duplicated_entry['title']} "
                    f"{duplicated_entry['location']}"
                )
                search_index_entries.remove(duplicated_entry)
                target_lang_entries.remove(duplicated_entry)

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
                if self.config.reconfigure_search:
                    self.reconfigure_search_duplicates(search_index_entries)
                # run the post_build event to rebuild the search index
                plugin.on_post_build(config=config)

    def reconfigure_files(
        self,
        files: Files,
        mkdocs_config: MkDocsConfig,
    ) -> Union[suffix.I18nFiles, folder.I18nFiles]:
        """ """
        if self.config.docs_structure == "suffix":
            create_i18n_file = suffix.create_i18n_file
            I18nFiles = suffix.I18nFiles
        else:
            create_i18n_file = folder.create_i18n_file
            I18nFiles = folder.I18nFiles
        i18n_src_uris = {}
        i18n_files = I18nFiles(self, [])
        i18n_alternate_src_uris = defaultdict(list)
        for file in files:
            # user provided files in docs_dir
            if is_relative_to(file.abs_src_path, mkdocs_config.docs_dir):
                i18n_file = create_i18n_file(
                    file,
                    self.current_language,
                    self.default_language,
                    self.all_languages,
                    mkdocs_config,
                )

                # user provided documentation page
                if i18n_file.is_documentation_page():
                    # never seen that file?
                    if i18n_file.norm_src_uri not in i18n_src_uris:
                        # best case scenario
                        # use the file since its locale is our current build language
                        if i18n_file.locale == self.current_language:
                            i18n_src_uris[i18n_file.norm_src_uri] = i18n_file
                            log.debug(
                                f"Use {i18n_file.locale} {i18n_file.localization} {i18n_file}"
                            )
                        # if locale is the default language AND default language fallback is enabled
                        # we are using a file that is not really our locale
                        elif (
                            self.config.fallback_to_default is True
                            and i18n_file.locale == self.default_language
                        ):
                            i18n_src_uris[i18n_file.norm_src_uri] = i18n_file
                            log.debug(
                                f"Use default {i18n_file.locale} {i18n_file.localization} {i18n_file}"
                            )
                            i18n_alternate_src_uris[i18n_file.norm_src_uri].append(file)
                        else:
                            log.debug(
                                f"Ignore {i18n_file.locale} {i18n_file.localization} {i18n_file}"
                            )
                            i18n_alternate_src_uris[i18n_file.norm_src_uri].append(file)

                    # we've seen that file already
                    else:
                        # override it only if this is our language
                        if i18n_file.locale == self.current_language:
                            # users should not add default non suffixed/folder files + suffixed/folder
                            # files when multiple languages are configured
                            if (
                                len(self.build_languages) > 1
                                and i18n_file.localization is not None
                                and i18n_src_uris[i18n_file.norm_src_uri].locale == i18n_file.locale
                            ):
                                raise Exception(
                                    f"Conflicting files for the default language '{self.default_language}': "
                                    f"choose either '{i18n_file.norm_src_uri}' or "
                                    f"'{i18n_src_uris[i18n_file.norm_src_uri].src_uri}' but not both"
                                )
                            i18n_src_uris[i18n_file.norm_src_uri] = i18n_file
                            log.debug(
                                f"Use localized {i18n_file.locale} {i18n_file.localization} {i18n_file}"
                            )
                        else:
                            log.debug(
                                f"Ignore {i18n_file.locale} {i18n_file.localization} {i18n_file}"
                            )
                            i18n_alternate_src_uris[i18n_file.norm_src_uri].append(file)

                # user provided asset
                else:
                    # never seen that file?
                    if i18n_file.norm_src_uri not in i18n_src_uris:
                        # best case scenario
                        # use the file since its locale is our current build language
                        if i18n_file.locale == self.current_language:
                            i18n_src_uris[i18n_file.norm_src_uri] = i18n_file
                            log.debug(
                                f"Use asset {i18n_file.locale} {i18n_file.localization} {i18n_file}"
                            )
                        # if locale is the default language AND default language fallback is enabled
                        # we are using a file that is not really our locale
                        elif (
                            self.config.fallback_to_default is True
                            and i18n_file.locale == self.default_language
                        ):
                            i18n_asset = create_i18n_file(
                                file,
                                self.default_language,
                                self.default_language,
                                self.all_languages,
                                mkdocs_config,
                            )
                            i18n_src_uris[i18n_file.norm_src_uri] = i18n_asset
                            log.debug(
                                f"Use asset default {i18n_asset.locale} {i18n_file.localization} {i18n_asset}"
                            )

                    # we've seen that file already
                    else:
                        # override it only if this is our language
                        if i18n_file.localization == self.current_language:
                            i18n_src_uris[i18n_file.norm_src_uri] = i18n_file
                            log.debug(
                                f"Use asset localized {i18n_file.locale} {i18n_file.localization} {i18n_file}"
                            )

            # theme (and overrides) files
            elif not file.is_documentation_page():
                i18n_files.append(file)
            else:
                log.warning(f"Unhandled file case - {file.src_uri}")

        # populate the resulting Files and keep track of all the alternates
        # that will be used by the sitemap.xml template
        for file in i18n_src_uris.values():
            if "index" in file.src_uri:
                log.debug(f"Selected {file.locale} {file.localization} {file}")
            i18n_files.append(file)

        # build the alternates for all the Files
        self.reconfigure_files_alternates(
            i18n_src_uris, i18n_alternate_src_uris, mkdocs_config, create_i18n_file
        )

        return i18n_files

    def reconfigure_files_alternates(
        self,
        i18n_src_uris,
        i18n_alternate_src_uris,
        mkdocs_config: MkDocsConfig,
        create_i18n_file: Union[suffix.create_i18n_file, folder.create_i18n_file],
    ):
        """
        Find and update the alternates of each file.
        """
        for build_lang in sorted(self.build_languages):
            for i18n_src_uri, i18n_file in i18n_src_uris.items():
                if build_lang not in i18n_file.alternates:
                    for alternate_file in i18n_alternate_src_uris.get(i18n_src_uri, []):
                        alternate_file = create_i18n_file(
                            alternate_file,
                            build_lang,
                            self.default_language,
                            self.all_languages,
                            mkdocs_config,
                        )
                        if alternate_file.locale == build_lang:
                            i18n_file.alternates[alternate_file.locale] = alternate_file
                            break
                    else:
                        # if fallbacking to default language is configured and we did not find
                        # an alternate for the build language, look for the default version of the file
                        if self.config.fallback_to_default is True:
                            for alternate_file in i18n_alternate_src_uris.get(i18n_src_uri, []):
                                alternate_file = create_i18n_file(
                                    alternate_file,
                                    build_lang,
                                    self.default_language,
                                    self.all_languages,
                                    mkdocs_config,
                                )
                                if alternate_file.locale == self.default_language:
                                    i18n_file.alternates[build_lang] = alternate_file
                                    break
                            else:
                                alternate_file = create_i18n_file(
                                    i18n_file,
                                    build_lang,
                                    self.default_language,
                                    self.all_languages,
                                    mkdocs_config,
                                )
                                if alternate_file.locale == self.default_language:
                                    i18n_file.alternates[build_lang] = alternate_file
        # uncomment to debug alternate selection
        # for i18n_src_uri, i18n_file in i18n_src_uris.items():
        #     print(" ")
        #     print(f"{i18n_src_uri=}")
        #     for build_lang, alternate_file in i18n_file.alternates.items():
        #         print(
        #             f"    {build_lang=} {alternate_file.src_uri=} {alternate_file.locale_alternate_of=} {alternate_file.src_uri=}"
        #         )

    def reconfigure_material_blog(self, nav: Navigation, mkdocs_config: MkDocsConfig, files: Files):
        """
        Since the material/blog plugin does modify the files structure and the navigation
        we need to override them and rebuild the blog/ part of it ourselves for now.

        See: https://github.com/squidfunk/mkdocs-material/issues/5909
        """
        if self.config.docs_structure == "suffix":
            create_i18n_file = suffix.create_i18n_file
        else:
            create_i18n_file = folder.create_i18n_file

        i18n_src_uris = {}
        i18n_alternate_src_uris = defaultdict(list)

        # at this point, the files have been cleaned up contrary to the
        # initial on_files run so it's harder to build the alternates
        for file in files:
            if is_relative_to(file.url, "blog/"):
                # get a localized version of the blog file
                i18n_file = create_i18n_file(
                    file,
                    self.current_language,
                    self.default_language,
                    self.all_languages,
                    mkdocs_config,
                )
                # used to rebuild blog alternates for the sitemap.xml and language switcher
                i18n_src_uris[i18n_file.norm_src_uri] = file
                i18n_alternate_src_uris[i18n_file.norm_src_uri].append(
                    File(
                        file.src_path,
                        mkdocs_config.docs_dir,
                        file.dest_path,
                        mkdocs_config.use_directory_urls,
                        dest_uri=file.dest_uri,
                        inclusion=file.inclusion,
                    )
                )
                # override blog related file specific properties in place
                file.abs_dest_path = i18n_file.abs_dest_path
                file.alternates = {self.current_language: file}
                file.dest_uri = i18n_file.dest_uri
                file.locale = i18n_file.locale
                file.locale_alternate_of = self.current_language
                file.norm_src_uri = i18n_file.norm_src_uri
                file.url = i18n_file._get_url(mkdocs_config.use_directory_urls)
                #
                if file.page:
                    file.page._set_canonical_url(mkdocs_config.get('site_url', None))

        # reconfigure blog files alternates to the best we can
        # since we are past the on_files event and files useless to the current language
        # have been filtered out and new ones got generated by the blog plugin,
        # we can't get the complete view of the alternates
        self.reconfigure_files_alternates(
            i18n_src_uris, i18n_alternate_src_uris, mkdocs_config, create_i18n_file
        )

        # update the per-language files store for template alternates
        self.i18n_files_per_language[self.current_language] = files.documentation_pages()

        return nav

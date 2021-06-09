import logging
import os
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

from mkdocs.commands.build import _build_page, _populate_page
from mkdocs.config.base import ValidationError
from mkdocs.config.config_options import Type
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.nav import get_navigation

try:
    from mkdocs.localization import install_translations
except ImportError:
    install_translations = None

try:
    import pkg_resources

    material_dist = pkg_resources.get_distribution("mkdocs-material")
    material_version = material_dist.version
    material_languages = [
        lang.split(".html")[0]
        for lang in material_dist.resource_listdir("material/partials/languages")
    ]
except Exception:
    material_languages = []
    material_version = None

log = logging.getLogger("mkdocs.plugins." + __name__)

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


class Locale(Type):
    """
    Locale Config Option

    Validate the locale config option against a given Python type.
    """

    def __init__(self, type_, length=None, **kwargs):
        super().__init__(type_, length=length, **kwargs)
        self._type = type_
        self.length = length

    def run_validation(self, value):
        value = super().run_validation(value)
        # check that str of dict keys corresponding to languages we are lower case
        # and have a minimal length
        if isinstance(value, str):
            if value.lower() != value:
                raise ValidationError(
                    "Language values must be ISO-639-1 lower case, "
                    f"received '{value}' expected '{value.lower()}'."
                )
        if isinstance(value, dict):
            for key in value:
                if key.lower() != key:
                    raise ValidationError(
                        "Language values must be ISO-639-1 lower case, "
                        f"received '{key}' expected '{key.lower()}'."
                    )
                elif len(key) != 2:
                    raise ValidationError(
                        "Language values must respect the ISO-639-1 (2-letter) "
                        f"format, received '{key}' of length '{len(key)}'."
                    )
        return value


class I18nFiles(Files):
    """
    This class extends MkDocs' Files class to support links and assets that
    have a translated locale suffix.

    This MkDocs relies on the file.src_path of pages and assets we have to
    derive the file.src_path and check for a possible .<locale>.<suffix> file
    to use instead of the link / asset referenced in the markdown source.
    """

    locale = None
    translated = False

    def __contains__(self, path):
        """
        Return a bool stipulating whether or not we found a translated version
        of the given path or the path itself.
        """
        expected_src_path = Path(path)
        expected_src_paths = [
            expected_src_path.with_suffix(f".{self.locale}{expected_src_path.suffix}"),
            expected_src_path.with_suffix(
                f".{self.default_locale}{expected_src_path.suffix}"
            ),
            expected_src_path,
        ]
        return any(filter(lambda s: Path(s) in expected_src_paths, self.src_paths))

    def get_file_from_path(self, path):
        """ Return a File instance with File.src_path equal to path. """
        expected_src_path = Path(path)
        expected_src_paths = [
            expected_src_path.with_suffix(f".{self.locale}{expected_src_path.suffix}"),
            expected_src_path.with_suffix(
                f".{self.default_locale}{expected_src_path.suffix}"
            ),
            expected_src_path,
        ]
        for src_path in filter(lambda s: Path(s) in expected_src_paths, self.src_paths):
            return self.src_paths.get(os.path.normpath(src_path))


class I18n(BasePlugin):

    config_scheme = (
        ("default_language", Locale(str, length=2, required=True)),
        ("languages", Locale(dict, required=True)),
        ("material_alternate", Type(bool, default=True, required=False)),
        ("nav_translations", Type(dict, default={}, required=False)),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.i18n_configs = {}
        self.i18n_files = defaultdict(list)
        self.i18n_navs = {}

    def _is_translation_for(self, src_path, language):
        return Path(src_path).suffixes == [f".{language}", Path(src_path).suffix]

    def _get_translated_page(self, page, language, config):
        # there is a specific translation file for this lang
        for lang in self.all_languages:
            if self._is_translation_for(page.src_path, lang):
                i18n_page = self._get_i18n_page(page, lang, config)
                break
        else:
            i18n_page = deepcopy(page)

        # setup and copy the file to the current language path
        i18n_page.dest_path = Path(f"/{language}/{i18n_page.dest_path}")
        i18n_page.abs_dest_path = Path(f"{config['site_dir']}/{i18n_page.dest_path}")
        i18n_page.url = (
            f"{language}/" if i18n_page.url == "." else f"{language}/{i18n_page.url}"
        )

        return i18n_page

    def _get_translated_asset(self, page, language, config, suffix):
        # there is a specific translation file for this lang
        for lang in self.all_languages:
            if self._is_translation_for(page.src_path, lang):
                i18n_page = self._get_i18n_asset(page, lang, config, suffix)
                break
        else:
            return page

        # setup and copy the file to the current language path
        i18n_page.dest_path = Path(f"/{language}/{i18n_page.dest_path}")
        i18n_page.abs_dest_path = Path(f"{config['site_dir']}/{i18n_page.dest_path}")
        i18n_page.url = (
            f"{language}/" if i18n_page.url == "." else f"{language}/{i18n_page.url}"
        )

        return i18n_page

    def _get_i18n_page(self, page, page_lang, config):
        i18n_page = deepcopy(page)
        i18n_page.abs_dest_path = Path(i18n_page.abs_dest_path)
        i18n_page.dest_path = Path(i18n_page.dest_path)
        i18n_page.name = str(Path(page.name).stem)
        if config.get("use_directory_urls") is False:
            i18n_page.dest_path = i18n_page.dest_path.with_name(
                i18n_page.name
            ).with_suffix(".html")
            i18n_page.abs_dest_path = i18n_page.abs_dest_path.with_name(
                i18n_page.name
            ).with_suffix(".html")
            i18n_page.url = page.url.replace(page.name, i18n_page.name) or "."
        else:
            # index files do not exhibit a named folder
            # whereas named files do!
            if i18n_page.name == "index":
                i18n_page.dest_path = i18n_page.dest_path.parent.with_suffix(".html")
                i18n_page.abs_dest_path = i18n_page.abs_dest_path.parent.with_suffix(
                    ".html"
                )
                i18n_page.url = str(Path(i18n_page.dest_path).parent.as_posix()) + "/"

            else:
                i18n_page.dest_path = i18n_page.dest_path.parent.with_suffix(
                    ""
                ).joinpath(i18n_page.dest_path.name)
                i18n_page.abs_dest_path = i18n_page.abs_dest_path.parent.with_suffix(
                    ""
                ).joinpath(i18n_page.abs_dest_path.name)
                i18n_page.url = str(Path(i18n_page.dest_path).parent.as_posix()) + "/"

        return i18n_page

    def _get_i18n_asset(self, page, page_lang, config, suffix):
        i18n_page = deepcopy(page)
        i18n_page.abs_dest_path = Path(i18n_page.abs_dest_path)
        i18n_page.dest_path = Path(i18n_page.dest_path)
        i18n_page.name = str(Path(page.name).stem)
        # root folder assets
        if i18n_page.dest_path.parent == Path("."):
            i18n_page.dest_path = Path(f"{i18n_page.name}{suffix}")
            i18n_page.abs_dest_path = Path(
                f"{i18n_page.abs_dest_path.parent}/{i18n_page.dest_path}"
            )
        else:
            i18n_page.dest_path = i18n_page.dest_path.parent.with_suffix("").joinpath(
                f"{i18n_page.name}{suffix}"
            )
            i18n_page.abs_dest_path = i18n_page.abs_dest_path.parent.with_suffix(
                ""
            ).joinpath(f"{i18n_page.name}{suffix}")
        i18n_page.url = str(Path(i18n_page.dest_path).as_posix())

        return i18n_page

    def _get_page_lang(self, page):
        for language in self.all_languages:
            if Path(page.src_path).suffixes == [
                f".{language}",
                Path(page.src_path).suffix,
            ]:
                return language
        return None

    def _get_page_from_paths(self, expected_paths, files):
        for expected_path in expected_paths:
            for page in files:
                if Path(page.src_path) == expected_path:
                    return page
        else:
            raise Exception(
                f"mkdocs-static-i18n is expecting one of the following files: {expected_paths}"
            )

    def _dict_replace_value(self, directory, old, new):
        """
        Return a copy of the given dict with value replaced.
        """
        x = {}
        for k, v in directory.items():
            if isinstance(v, dict):
                v = self._dict_replace_value(v, old, new)
            elif isinstance(v, list):
                v = self._list_replace_value(v, old, new)
            elif isinstance(v, str) or isinstance(v, Path):
                if str(v) == str(old):
                    v = new
                v = str(Path(v))
            x[k] = v
        return x

    def _list_replace_value(self, listing, old, new):
        """
        Return a copy of the given list with value replaced.
        """
        x = []
        for e in listing:
            if isinstance(e, list):
                e = self._list_replace_value(e, old, new)
            elif isinstance(e, dict):
                e = self._dict_replace_value(e, old, new)
            elif isinstance(e, str) or isinstance(e, Path):
                if str(e) == str(old):
                    e = new
                e = str(Path(e))
            x.append(e)
        return x

    def _get_base_path(self, page):
        """
        Return the path of the given page without any suffix.
        """
        page_lang = self._get_page_lang(page)
        if page_lang is None:
            base_path = Path(page.src_path).with_suffix("")
        else:
            base_path = Path(page.src_path).with_suffix("").with_suffix("")
        return base_path

    def on_config(self, config, **kwargs):
        """
        Enrich configuration with language specific knowledge.
        """
        self.default_language = self.config.get("default_language")
        self.all_languages = set(
            [self.default_language] + list(self.config["languages"])
        )
        # Support for mkdocs-material>=7.1.0 language selector
        if self.config["material_alternate"]:
            if material_version and material_version >= "7.1.0":
                if not config["extra"].get("alternate") or kwargs.get("force"):
                    # Add index.html file name when used with
                    # use_directory_urls = True
                    link_suffix = ""
                    if config.get("use_directory_urls") is False:
                        link_suffix = "index.html"
                    config["extra"]["alternate"] = [
                        {
                            "name": self.config["languages"].get(
                                self.config["default_language"],
                                self.config["default_language"],
                            ),
                            "link": f"./{link_suffix}",
                            "lang": self.config["default_language"],
                        }
                    ]
                    for language in self.all_languages:
                        if language == self.config["default_language"]:
                            continue
                        config["extra"]["alternate"].append(
                            {
                                "name": self.config["languages"][language],
                                "link": f"./{language}/{link_suffix}",
                                "lang": language,
                            }
                        )
        # Support for the search plugin lang
        if "search" in config["plugins"]:
            search_langs = config["plugins"]["search"].config["lang"] or []
            for language in self.all_languages:
                if language in LUNR_LANGUAGES:
                    if language not in search_langs:
                        search_langs.append(language)
                        log.info(
                            f"Adding '{language}' to the 'plugins.search.lang' option"
                        )
                else:
                    log.warning(
                        f"Language '{language}' is not supported by "
                        f"lunr.js, not setting it in the 'plugins.search.lang' option"
                    )
        return config

    def on_files(self, files, config):
        """
        Construct the main + lang specific file tree which will be used to
        generate the navigation for the default site and per language.
        """
        main_files = I18nFiles([])
        main_files.default_locale = self.default_language
        main_files.locale = self.default_language
        for language in self.all_languages:
            self.i18n_configs[language] = deepcopy(config)
            self.i18n_files[language] = I18nFiles([])
            self.i18n_files[language].default_locale = self.default_language
            self.i18n_files[language].locale = language
            # there can be only one instance of the search plugin because
            # it is hardcoded in the JS worker sources
            if "search" in config["plugins"]:
                self.i18n_configs[language]["plugins"]["search"] = config["plugins"][
                    "search"
                ]

        base_paths = set()
        for fileobj in files:
            base_path = self._get_base_path(fileobj)
            if base_path in base_paths:
                continue

            suffix = Path(fileobj.src_path).suffix

            # main expects .md or .default_language.md
            main_expects = [
                Path(f"{base_path}{suffix}"),
                Path(f"{base_path}.{self.default_language}{suffix}"),
            ]
            main_page = self._get_page_from_paths(main_expects, files)

            page_lang = self._get_page_lang(main_page)
            if page_lang is None:
                main_files.append(main_page)
            else:
                if fileobj in files.documentation_pages():
                    # .md documentation files
                    main_files.append(self._get_i18n_page(main_page, page_lang, config))
                else:
                    # any other .<language>.<suffix> files
                    main_files.append(
                        self._get_i18n_asset(main_page, page_lang, config, suffix)
                    )

            for language in self.all_languages:
                lang_expects = [
                    Path(f"{base_path}.{language}{suffix}"),
                    Path(f"{base_path}.{self.default_language}{suffix}"),
                    Path(f"{base_path}{suffix}"),
                ]
                lang_page = self._get_page_from_paths(lang_expects, files)

                page_lang = self._get_page_lang(lang_page)
                if fileobj in files.documentation_pages():
                    # .md documentation files
                    self.i18n_files[language].append(
                        self._get_translated_page(lang_page, language, config)
                    )
                else:
                    # any other .<language>.<suffix> files
                    self.i18n_files[language].append(
                        self._get_translated_asset(lang_page, language, config, suffix)
                    )

                base_paths.add(base_path)

        # these comments are here to help me debug later if needed
        # print([{p.src_path: p.url} for p in main_files.documentation_pages()])
        # print([{p.src_path: p.url} for p in self.i18n_files["en"].documentation_pages()])
        # print([{p.src_path: p.url} for p in self.i18n_files["fr"].documentation_pages()])
        # print([{p.src_path: p.url} for p in main_files.static_pages()])
        # print([{p.src_path: p.url} for p in self.i18n_files["en"].static_pages()])
        # print([{p.src_path: p.url} for p in self.i18n_files["fr"].static_pages()])

        return main_files

    def _fix_config_navigation(self, language, files):
        """
        When a static navigation is set in mkdocs.yml a user will usually
        structurate its navigation using the main (default language)
        documentation markdown pages.

        This function localizes the given pages to their translated
        counterparts if available.
        """
        for i18n_page in files.documentation_pages():
            if Path(i18n_page.src_path).suffixes == [f".{language}", ".md"]:
                base_path = self._get_base_path(i18n_page)
                config_path_expects = [
                    base_path.with_suffix(".md"),
                    base_path.with_suffix(f".{self.default_language}.md"),
                ]
                for config_path in config_path_expects:
                    self.i18n_configs[language]["nav"] = self._list_replace_value(
                        self.i18n_configs[language]["nav"],
                        config_path,
                        i18n_page.src_path,
                    )

    def _translate_navigation(self, language, nav):
        translated_nav = self.config["nav_translations"].get(language, {})
        if translated_nav:
            for item in nav:
                if hasattr(item, "title") and item.title in translated_nav:
                    item.title = translated_nav[item.title]
                if hasattr(item, "children") and item.children:
                    self._translate_navigation(language, item.children)

    def on_nav(self, nav, config, files):
        """
        Translate i18n aware navigation to honor the 'nav_translations' option.
        """
        if not files.translated and self.config["nav_translations"].get(files.locale):
            log.info(f"Translating navigation to {files.locale}")
            self._translate_navigation(files.locale, nav)
            files.translated = True
        return nav

    def _fix_search_duplicates(self, language, search_plugin):
        """
        We want to avoid indexing the same pages twice if the default language
        has its own version built as well as the /language version too as this
        would pollute the search results.

        When this happens, we favor the default language location if its
        content is the same as its /language counterpart.
        """
        entries = deepcopy(search_plugin.search_index._entries)
        for entry in entries:
            if entry["location"].startswith(f"{language}/"):
                for s_entry in search_plugin.search_index._entries:
                    expected_locations = [
                        f"{language}/{s_entry['location']}",
                        f"{language}/{s_entry['location'].rstrip('/')}",
                        f"{language}/{s_entry['location'].replace('/#', '#')}",
                    ]
                    if entry["location"] in expected_locations:
                        if entry["text"] == s_entry["text"]:
                            search_plugin.search_index._entries.remove(entry)

    def on_post_build(self, config):
        """
        Derived from mkdocs commands build function.

        We build every language on its own directory.
        """
        dirty = False
        search_plugin = config["plugins"].get("search")
        for language in self.config.get("languages"):
            log.info(f"Building {language} documentation")

            if self.i18n_configs[language]["nav"]:
                self._fix_config_navigation(language, self.i18n_files[language])

            self.i18n_navs[language] = get_navigation(
                self.i18n_files[language], self.i18n_configs[language]
            )

            config = self.i18n_configs[language]
            env = self.i18n_configs[language]["theme"].get_env()
            files = self.i18n_files[language]
            nav = self.i18n_navs[language]

            # TODO: check if messing with site_dir wouldn't be easier than
            # changing file dest_paths etc
            # config["site_dir"] += "/fr"

            # Support mkdocs-material theme language
            if config["theme"].name == "material":
                if language in material_languages:
                    config["theme"].language = language
                else:
                    log.warning(
                        f"Language {language} is not supported by "
                        f"mkdocs-material=={material_version}, not setting "
                        "the 'theme.language' option"
                    )

            # Run `nav` plugin events.
            # This is useful to be compatible with nav order changing plugins
            # such as mkdocs-awesome-pages-plugin
            nav = config["plugins"].run_event("nav", nav, config=config, files=files)

            files.copy_static_files(dirty=dirty)

            for file in files.documentation_pages():
                _populate_page(file.page, config, files, dirty)

            for file in files.documentation_pages():
                _build_page(file.page, config, files, nav, env, dirty)

            # Update the search plugin index with language pages
            if search_plugin:
                if (
                    language == self.default_language
                    and self.default_language in self.config["languages"]
                ):
                    self._fix_search_duplicates(language, search_plugin)
                search_plugin.on_post_build(config)

import logging
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

from mkdocs.commands.build import _build_page, _populate_page
from mkdocs.config.base import ValidationError
from mkdocs.config.config_options import Type
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.nav import get_navigation

log = logging.getLogger(__name__)


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
                    f"Language values should be lower case, received '{value}' "
                    f"expected '{value.lower()}'."
                )
            elif len(value) < 2:
                raise ValidationError(
                    f"Language values should be at least two characters long, "
                    f"received '{value}' of length '{len(value)}'."
                )
        if isinstance(value, dict):
            for key in value:
                if key.lower() != key:
                    raise ValidationError(
                        f"Language values should be lower case, received '{key}' "
                        f"expected '{key.lower()}'."
                    )
                elif len(key) < 2:
                    raise ValidationError(
                        f"Language values should be at least two characters long, "
                        f"received '{key}' of length '{len(key)}'."
                    )
        return value


class I18n(BasePlugin):

    config_scheme = (
        ("default_language", Locale(str, required=True)),
        ("languages", Locale(dict, required=True)),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.i18n_files = defaultdict(list)
        self.i18n_navs = {}

    def _is_translation_for(self, src_path, language):
        return Path(src_path).suffixes == [f".{language}", ".md"]

    def _get_translated_page(self, page, language, config):
        i18n_page = deepcopy(page)

        # there is a specific translation file for this lang
        for lang in self.all_languages:
            if self._is_translation_for(i18n_page.src_path, lang):
                i18n_page.name = page.name.replace(f".{lang}", "")
                if config.get("use_directory_urls") is False:
                    i18n_page.dest_path = i18n_page.dest_path.replace(
                        page.name, i18n_page.name
                    )
                    i18n_page.abs_dest_path = i18n_page.abs_dest_path.replace(
                        page.name, i18n_page.name
                    )
                    i18n_page.url = (
                        i18n_page.url.replace(page.name, i18n_page.name) or "."
                    )
                else:
                    i18n_page.dest_path = i18n_page.dest_path.replace(
                        f"{page.name}/", ""
                    )
                    i18n_page.abs_dest_path = i18n_page.abs_dest_path.replace(
                        f"{page.name}/", ""
                    )
                    i18n_page.url = i18n_page.url.replace(f"{page.name}/", "") or "."
                break

        # setup and copy the file to the current language path
        i18n_page.dest_path = f"/{language}/{i18n_page.dest_path}"
        i18n_page.abs_dest_path = i18n_page.abs_dest_path.replace(
            config["site_dir"], f"{config['site_dir']}/{language}"
        )
        i18n_page.url = (
            f"{language}/" if i18n_page.url == "." else f"{language}/{i18n_page.url}"
        )

        return i18n_page

    def _get_non_translated_page(self, page, page_lang, config):
        i18n_page = deepcopy(page)
        i18n_page.name = page.name.replace(f".{page_lang}", "")
        if config.get("use_directory_urls") is False:
            i18n_page.dest_path = page.dest_path.replace(f"{page.name}", i18n_page.name)
            i18n_page.abs_dest_path = page.abs_dest_path.replace(
                f"{page.name}", i18n_page.name
            )
            i18n_page.url = page.url.replace(page.name, i18n_page.name) or "."
        else:
            i18n_page.dest_path = page.dest_path.replace(f"{page.name}/", "")
            i18n_page.abs_dest_path = page.abs_dest_path.replace(f"{page.name}/", "")
            i18n_page.url = page.url.replace(f"{page.name}/", "") or "."

        return i18n_page

    def _get_page_lang(self, page):
        for language in self.all_languages:
            if Path(page.src_path).suffixes == [f".{language}", ".md"]:
                return language
        return None

    def _get_page_from_paths(self, expected_paths, files):
        for expected_path in expected_paths:
            for page in files.documentation_pages():
                if Path(page.src_path) == expected_path:
                    return page
        else:
            raise Exception(
                f"mkdocs-static-i18n is expecting one of the following files: {expected_paths}"
            )

    def on_files(self, files, config):
        """
        Construct the main + lang specific file tree which will be used to
        generate the navigation for the default site and per language.
        """
        if self.i18n_files:
            # avoids calling ourselves multiple times via on_post_build
            return files

        default_language = self.config.get("default_language")
        self.all_languages = set([default_language] + list(self.config["languages"]))

        main_files = Files([])
        for language in self.all_languages:
            self.i18n_files[language] = Files([])

        for obj in files:
            if obj not in files.documentation_pages():
                main_files.append(obj)
                for language in self.all_languages:
                    self.i18n_files[language].append(obj)

        base_paths = set()
        for page in files.documentation_pages():
            page_lang = self._get_page_lang(page)
            if page_lang is None:
                base_path = Path(page.src_path).with_suffix("")
            else:
                base_path = Path(page.src_path).with_suffix("").with_suffix("")

            if base_path in base_paths:
                continue

            # main expects .md or .default_language.md
            main_expects = [
                base_path.with_suffix(".md"),
                base_path.with_suffix(f".{default_language}.md"),
            ]
            main_page = self._get_page_from_paths(main_expects, files)

            page_lang = self._get_page_lang(main_page)
            if page_lang is None:
                main_files.append(main_page)
            else:
                main_files.append(
                    self._get_non_translated_page(main_page, page_lang, config)
                )

            for language in self.all_languages:
                lang_expects = [
                    base_path.with_suffix(f".{language}.md"),
                    base_path.with_suffix(f".{default_language}.md"),
                    base_path.with_suffix(".md"),
                ]
                lang_page = self._get_page_from_paths(lang_expects, files)

                page_lang = self._get_page_lang(lang_page)
                self.i18n_files[language].append(
                    self._get_translated_page(lang_page, language, config)
                )

            base_paths.add(base_path)

        # these comments are here to help me debug later if needed
        # print([{p.src_path: p.url} for p in main_files.documentation_pages()])
        # print([{p.src_path: p.url} for p in self.i18n_files["en"].documentation_pages()])
        # print([{p.src_path: p.url} for p in self.i18n_files["fr"].documentation_pages()])

        return main_files

    def on_nav(self, nav, config, files):
        """"""
        if self.i18n_navs:
            # avoids calling ourselves multiple times via on_post_build
            return nav
        for language, files in self.i18n_files.items():
            self.i18n_navs[language] = get_navigation(files, config)
            if nav.homepage is not None:
                self.i18n_navs[language].homepage = deepcopy(nav.homepage)
                self.i18n_navs[
                    language
                ].homepage.file.url = f"{language}/{nav.homepage.file.url}"
        return nav

    def on_post_build(self, config):
        """
        Derived from mkdocs commands build function.

        We build every language on its own directory.
        """
        dirty = False
        env = config["theme"].get_env()
        for language in self.config.get("languages"):
            log.info(f"Building {language} documentation")

            files = self.i18n_files[language]
            nav = self.i18n_navs[language]

            # Run `nav` plugin events.
            # This is useful to be compatible with nav order changing plugins
            # such as mkdocs-awesome-pages-plugin
            nav = config["plugins"].run_event("nav", nav, config=config, files=files)

            for file in files.documentation_pages():
                _populate_page(file.page, config, files, dirty)

            for file in self.i18n_files[language].documentation_pages():
                _build_page(file.page, config, files, nav, env, dirty)

    def on_page_context(self, context, page, config, nav):
        """
        mkdocs-material search context i18n support
        """
        for language in self.config.get("languages"):
            if page.url.startswith(f"{language}/"):
                if config["theme"].name == "material":
                    context["config"]["theme"].language = language
                break
        return context

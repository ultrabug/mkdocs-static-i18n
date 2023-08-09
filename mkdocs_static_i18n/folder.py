import os
from collections import defaultdict
from pathlib import Path, PurePath
from typing import Optional

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.files import File, Files

from mkdocs_static_i18n import is_relative_to

log = get_plugin_logger(__name__)


def create_i18n_file(
    file: File,
    current_language: str,
    default_language: str,
    all_languages: list,
    config: MkDocsConfig,
) -> File:
    log.debug(f"reconfigure {file}")

    # create a new File instance that we can turn into an i18n file
    file = File(
        file.src_path,
        config.docs_dir,
        file.dest_path,
        config.use_directory_urls,
        dest_uri=file.dest_uri,
        inclusion=file.inclusion,
    )

    file_dest_path = Path(file.dest_path)
    file_locale = default_language
    is_asset = False

    for language in all_languages:
        if PurePath(file.src_path).is_relative_to(language):
            file_locale = language
            break
    else:
        is_asset = True

    # README.html should be renamed to index.html
    if file_dest_path.name.endswith("README.html"):
        file_dest_path = file_dest_path.with_name("index.html")

    if is_asset:
        # don't change assets (root) paths
        pass
    elif file_locale != current_language:
        if PurePath(file_dest_path).is_relative_to(file_locale):
            # we have to change the output folder
            file.dest_path = PurePath(
                PurePath(current_language) / PurePath(file_dest_path).relative_to(file_locale)
            ).as_posix()
        elif current_language != default_language:
            file.dest_path = PurePath(
                PurePath(current_language) / PurePath(file_dest_path)
            ).as_posix()
    elif file_locale == default_language:
        # we check that we are relative since we also accept other non localized files (assets)
        if PurePath(file_dest_path).is_relative_to(file_locale):
            # we have to change the output folder to nothing
            file.dest_path = PurePath(file_dest_path).relative_to(file_locale).as_posix()
        elif current_language != default_language:
            file.dest_path = PurePath(
                PurePath(current_language) / PurePath(file_dest_path)
            ).as_posix()
    file.abs_dest_path = os.path.normpath(os.path.join(config.site_dir, file.dest_path))

    # assure a valid name for the Page.is_index check
    if file.name == "README":
        file.name = "index"

    # update the url in case we played with the folder structure
    file.url = file._get_url(config.use_directory_urls)

    # save some i18n metadata
    # alternates should list themselves
    file.alternates = {current_language: file}
    file.locale = file_locale
    file.locale_alternate_of = current_language
    file.is_asset = is_asset

    log.debug(f"reconfigure {file} from locale {file_locale}")

    return file


class I18nFiles(Files):
    """
    We need to override Files to handle the automagic discovery of resources allowing
    users to not specify their suffixed version of the resource (think image).

    Example: french page displaying image.fr.png can use [my french img](image.png)

    This is made possible by overriding 'get_file_from_path' below.
    """

    def __init__(self, plugin, files: Files) -> None:
        super().__init__(files)
        self.plugin = plugin

    def get_file_from_path(self, path: str) -> Optional[File]:
        """
        Used by mkdocs.structure.nav.get_navigation to find resources linked in markdown.
        """
        expected_src_uri = PurePath(path)
        expected_src_uris = []
        if expected_src_uri.is_relative_to(self.plugin.current_language):
            expected_src_uris.append(expected_src_uri.relative_to(self.plugin.current_language))
        if expected_src_uri.is_relative_to(self.plugin.default_language):
            expected_src_uris.append(expected_src_uri.relative_to(self.plugin.default_language))
        expected_src_uris.append(expected_src_uri)
        for src_uri in expected_src_uris:
            file = self.src_uris.get(src_uri.as_posix())
            if file:
                return file
        else:
            return None

    def update_files_alternates(
        self, i18n_dest_uris, i18n_alternate_dest_uris, mkdocs_config: MkDocsConfig
    ):
        """
        Find and update the alternates of each file.
        """
        for build_lang in sorted(self.plugin.build_languages):
            for i18n_dest_uri, i18n_file in i18n_dest_uris.items():
                if build_lang not in i18n_file.alternates:
                    for alternate_file in i18n_alternate_dest_uris.get(i18n_dest_uri, []):
                        alternate_file = create_alternate_from(
                            alternate_file, build_lang, self.plugin, mkdocs_config
                        )
                        if alternate_file.locale == build_lang:
                            i18n_file.alternates[alternate_file.locale] = alternate_file
                            break
                    else:
                        # if fallbacking to default language is configured and we did not find
                        # an alternate for the build language, look for the default version of the file
                        if self.plugin.config.fallback_to_default is True:
                            for alternate_file in i18n_alternate_dest_uris.get(i18n_dest_uri, []):
                                alternate_file = create_alternate_from(
                                    alternate_file, build_lang, self.plugin, mkdocs_config
                                )
                                if alternate_file.locale == self.plugin.default_language:
                                    i18n_file.alternates[build_lang] = alternate_file
                                    break
                            else:
                                alternate_file = create_alternate_from(
                                    i18n_file, build_lang, self.plugin, mkdocs_config
                                )
                                if alternate_file.locale == self.plugin.default_language:
                                    i18n_file.alternates[build_lang] = alternate_file
        # uncomment to debug alternate selection
        # for i18n_dest_uri, i18n_file in i18n_dest_uris.items():
        #     print(" ")
        #     print(f"{i18n_dest_uri=}")
        #     for build_lang, alternate_file in i18n_file.alternates.items():
        #         print(
        #             f"    {build_lang=} {alternate_file.src_uri=} {alternate_file.locale_alternate_of=} {alternate_file.dest_uri=}"
        #         )


def create_alternate_from(file, alternate_language, i18n_plugin, mkdocs_config: MkDocsConfig):
    alternate_file = create_i18n_file(
        file,
        alternate_language,
        i18n_plugin.default_language,
        i18n_plugin.all_languages,
        mkdocs_config,
    )
    return alternate_file


def reconfigure_navigation(i18n_plugin, nav):
    """
    Remove the Section(title='En') language sections.
    """
    items = []
    for section in filter(lambda i: i.is_top_level and i.is_section, nav.items):
        if (
            section.title == i18n_plugin.current_language.capitalize()
            or i18n_plugin.default_language.capitalize()
        ):
            items.extend(section.children)
    nav.items = items
    # [Page(title=[blank], url='/mkdocs-static-i18n/fr/'), Section(title='Topic1'), Section(title='Topic2'), Section(title='French only'), Section(title='English default')]
    # =>
    # [Page(title=[blank], url='/mkdocs-static-i18n/fr/'), Section(title='English default'), Section(title='French only'), Section(title='Topic1'), Section(title='Topic2')]
    nav.items.sort(key=lambda x: x.title if x.title else "")
    return nav


def on_files(i18n_plugin, files: Files, mkdocs_config: MkDocsConfig) -> I18nFiles:
    """ """
    i18n_dest_uris = {}
    i18n_files = I18nFiles(i18n_plugin, [])
    i18n_alternate_dest_uris = defaultdict(list)
    for file in files:
        # documentation files
        if is_relative_to(file.abs_src_path, mkdocs_config.docs_dir):
            i18n_file = create_i18n_file(
                file,
                i18n_plugin.current_language,
                i18n_plugin.default_language,
                i18n_plugin.all_languages,
                mkdocs_config,
            )
            # this file is from the target language to build
            if PurePath(file.src_path).is_relative_to(i18n_plugin.current_language):
                i18n_dest_uris[i18n_file.dest_uri] = i18n_file
                log.debug(f"Use localized {i18n_file.locale} {i18n_file}")
            elif PurePath(file.src_path).is_relative_to(i18n_plugin.default_language):
                if i18n_file.dest_uri not in i18n_dest_uris:
                    i18n_dest_uris[i18n_file.dest_uri] = i18n_file
                    log.debug(f"Use default {i18n_file.locale} {i18n_file}")
                i18n_alternate_dest_uris[i18n_file.dest_uri].append(file)
            else:
                # root / assets files
                if i18n_file.is_asset is True:
                    i18n_dest_uris[i18n_file.dest_uri] = i18n_file
                    log.debug(f"Use asset {i18n_file.locale} {i18n_file}")

        # theme (and overrides) files
        elif i18n_plugin.is_default_language_build or file.src_uri.startswith("assets/"):
            i18n_files.append(file)

    # populate the resulting Files and keep track of all the alternates
    # that will be used by the sitemap.xml template
    for file in i18n_dest_uris.values():
        i18n_files.append(file)

    # build the alternates for all the Files
    i18n_files.update_files_alternates(i18n_dest_uris, i18n_alternate_dest_uris, mkdocs_config)

    return i18n_files

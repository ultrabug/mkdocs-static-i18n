import os
from pathlib import Path, PurePath
from typing import Optional

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.files import File, Files

from mkdocs_static_i18n import is_relative_to
from mkdocs_static_i18n.config import RE_LOCALE

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
    file_localization = None

    for language in all_languages:
        if is_relative_to(file.src_path, language):
            file_locale = language
            file_localization = language
            break
        else:
            # maybe the language folder is present BUT not configured in the plugin.languages yet
            # so we use the locale regex to guess that it's a localization folder
            maybe_file_locale = PurePath(file.src_path).parts[0]
            if RE_LOCALE.match(maybe_file_locale):
                file_locale = maybe_file_locale
                file_localization = maybe_file_locale
                break

    # README.html should be renamed to index.html
    if file_dest_path.name.endswith("README.html"):
        file_dest_path = file_dest_path.with_name("index.html")

    if file_locale != current_language:
        if is_relative_to(file_dest_path, file_locale):
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
        if is_relative_to(file_dest_path, file_locale):
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
    file.localization = file_localization

    # compute the normalized (non localized) src_uri
    file.norm_src_uri = file.src_uri
    if file.localization:
        file.norm_src_uri = PurePath(file.src_uri).relative_to(file.localization).as_posix()

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
        if expected_src_uri == PurePath("."):
            expected_src_uri = PurePath("index.md")

        expected_src_uris: list[PurePath] = []

        # non localized paths detection (root)
        if is_relative_to(expected_src_uri, self.plugin.current_language):
            # First add current_code/path
            # Second add default_code/path (fallback)
            # Last add path without prefix
            resolved_path = expected_src_uri.relative_to(self.plugin.current_language)
            expected_src_uris.append(expected_src_uri)
            if self.plugin.config.fallback_to_default is True:
                expected_src_uris.append(PurePath(self.plugin.default_language) / resolved_path)
            expected_src_uris.append(resolved_path)
        elif is_relative_to(expected_src_uri, self.plugin.default_language):
            # First add default_code/path
            # Second add current_code/path (fallback)
            # Last add path without prefix
            resolved_path = expected_src_uri.relative_to(self.plugin.default_language)
            expected_src_uris.append(expected_src_uri)
            if self.plugin.config.fallback_to_default is True:
                expected_src_uris.append(PurePath(self.plugin.current_language) / resolved_path)
            expected_src_uris.append(resolved_path)
        # localized paths detection
        else:
            # First add current_code/path
            # Second add default_code/path (fallback)
            # Last add path without modification
            expected_src_uris.append(PurePath(self.plugin.current_language) / expected_src_uri)
            if self.plugin.config.fallback_to_default is True:
                expected_src_uris.append(PurePath(self.plugin.default_language) / expected_src_uri)
            expected_src_uris.append(expected_src_uri)

        for src_uri in expected_src_uris:
            file = self.src_uris.get(src_uri.as_posix())
            if file:
                return file
        else:
            return None


def reconfigure_navigation(i18n_plugin, nav):
    """
    Remove the Section(title='En') language sections.
    """
    items = []
    for section in filter(lambda i: i.is_top_level and i.is_section, nav.items):
        if (
            section.title == i18n_plugin.current_language.capitalize()
            or section.title == i18n_plugin.default_language.capitalize()
        ):
            items.extend(section.children)
    if items:
        nav.items = items
        # [Page(title=[blank], url='/mkdocs-static-i18n/fr/'), Section(title='Topic1'), Section(title='Topic2'), Section(title='French only'), Section(title='English default')]
        # =>
        # [Page(title=[blank], url='/mkdocs-static-i18n/fr/'), Section(title='English default'), Section(title='French only'), Section(title='Topic1'), Section(title='Topic2')]
        nav.items.sort(key=lambda x: x.title if x.title else "")
    return nav

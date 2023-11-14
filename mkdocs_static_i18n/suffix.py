import os
from pathlib import Path, PurePath
from typing import Optional
from urllib.parse import quote as urlquote

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.files import File, Files

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
    locale_site_dir = current_language if current_language != default_language else ""

    try:
        file_locale = Path(file.name).suffixes.pop(-1).replace(".", "")
        # the file_locale must be a valid language locale code that we check on the
        # configured languages (validated by config) or using the locale regex in case
        # users have localized files but not configured them on the plugin.languages yet
        if file_locale in all_languages or RE_LOCALE.match(file_locale):
            file_dest_path_no_suffix = Path(file_dest_path.parent) / Path(
                file_dest_path.stem
            ).with_suffix("")
            file_dest_path = Path(f"{file_dest_path_no_suffix}{file_dest_path.suffix}")
            # file name suffixed by locale, remove it
            file.name = Path(file.name).stem
            # store file localization
            file_localization = file_locale
        else:
            file_locale = default_language
    except IndexError:
        pass

    if config.use_directory_urls and file_localization:
        if file_dest_path.parent != Path("."):
            parent_dest_path_no_suffix = file_dest_path.parent.with_suffix("")
            file_dest_path = parent_dest_path_no_suffix / file_dest_path.name
            # named index.lang.md get transformed to index.lang.md/index.md
            # so we need to remove that named folder
            if file_dest_path.parent.name in ["index", "README"]:
                file_dest_path = file_dest_path.parent.parent / file_dest_path.name

    # README.html should be renamed to index.html
    if file_dest_path.name.endswith("README.html"):
        file_dest_path = file_dest_path.with_name("index.html")

    if locale_site_dir:
        file.dest_path = Path(locale_site_dir) / file_dest_path
    else:
        file.dest_path = file_dest_path
    file.abs_dest_path = os.path.normpath(os.path.join(config.site_dir, file.dest_path))

    # assure a valid name for the Page.is_index check
    if file.name == "README":
        file.name = "index"

    # update the url in case we played with the folder structure
    file.url = file._get_url(config.use_directory_urls)

    # fix the url
    if locale_site_dir:
        if PurePath(file.url).as_posix() == ".":
            file.url = urlquote(locale_site_dir + "/")

    # save some i18n metadata
    # alternates should list themselves
    file.alternates = {current_language: file}
    file.locale = file_locale
    file.locale_alternate_of = current_language
    file.localization = file_localization

    # compute the normalized (non localized) src_uri
    file.norm_src_uri = file.src_uri
    if file.localization:
        file.norm_src_uri = file.src_uri.replace(f".{file.localization}", "", 1)

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
        expected_src_uris = [
            expected_src_uri.with_suffix(
                f".{self.plugin.current_language}{expected_src_uri.suffix}"
            ),
            expected_src_uri.with_suffix(
                f".{self.plugin.default_language}{expected_src_uri.suffix}"
            ),
            expected_src_uri,
        ]
        for src_uri in expected_src_uris:
            file = self.src_uris.get(src_uri.as_posix())
            if file:
                return file
        else:
            return None

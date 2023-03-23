import logging
import os
from pathlib import Path, PurePath
from urllib.parse import quote as urlquote

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files

log = logging.getLogger("mkdocs.plugins." + __name__)


def reconfigure_file(
    file: File,
    current_language: str,
    default_language: str,
    all_languages: list,
    config: MkDocsConfig,
) -> File:
    log.debug(f"reconfigure {file}")
    file_dest_path = Path(file.dest_path)
    file_locale = default_language
    locale_site_dir = current_language if current_language != default_language else ""

    try:
        file_locale = Path(file.name).suffixes.pop(-1).replace(".", "")
        if file_locale in all_languages:
            file_dest_path_no_suffix = Path(file_dest_path.parent) / Path(
                file_dest_path.stem
            ).with_suffix("")
            file_dest_path = Path(f"{file_dest_path_no_suffix}{file_dest_path.suffix}")
        else:
            file_locale = default_language
    except IndexError:
        pass

    if config.use_directory_urls:
        if file_dest_path.parent != Path("."):
            parent_dest_path_no_suffix = file_dest_path.parent.with_suffix("")
            file_dest_path = parent_dest_path_no_suffix / file_dest_path.name
            # named index.lang.md get transformed to index.lang.md/index.md
            # so we need to remove that named folder
            if file_dest_path.parent.name in ["index", "README"]:
                file_dest_path = file_dest_path.parent.parent / file_dest_path.name

    if locale_site_dir:
        file.dest_path = Path(locale_site_dir) / file_dest_path
    else:
        file.dest_path = file_dest_path
    file.abs_dest_path = os.path.normpath(os.path.join(config.site_dir, file.dest_path))
    file.name = Path(file_dest_path).stem

    # update the url in case we played with the folder structure
    file.url = file._get_url(config.use_directory_urls)

    # fix the url
    if locale_site_dir:
        if file.url == "./":
            file.url = urlquote(locale_site_dir + "/")

    # save some i18n metadata
    file.alternates = {}
    file.locale = file_locale

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

    def get_file_from_path(self, path: str):
        """
        Used by mkdocs.structure.nav.get_navigation to find resources linked in markdown.
        """
        expected_src_uri = PurePath(path)
        expected_src_uris = [
            expected_src_uri.with_suffix(
                f".{self.plugin.current_language}{expected_src_uri.suffix}"
            ),
            expected_src_uri.with_suffix(
                f".{self.plugin.default_language}{expected_src_uri.suffix}"
            ),
            expected_src_uri,
        ]
        for src_uri in filter(lambda s: Path(s) in expected_src_uris, self.src_uris):
            return self.src_uris.get(os.path.normpath(src_uri))


def on_files(self, files, config):
    """ """
    i18n_dest_uris = {}
    i18n_files = I18nFiles(self, [])
    for file in files:
        # documentation files
        if Path(file.abs_src_path).is_relative_to(config.docs_dir):
            i18n_file = reconfigure_file(
                file,
                self.current_language,
                self.default_language,
                self.all_languages,
                config,
            )

            # never seen that file?
            if i18n_file.dest_uri not in i18n_dest_uris:
                # best case scenario
                # use the file since its locale is our current build language
                if i18n_file.locale == self.current_language:
                    i18n_dest_uris[i18n_file.dest_uri] = i18n_file
                    log.debug(f"Use {i18n_file.locale} {i18n_file}")
                # if locale is the default language AND default language fallback is enabled
                # we are using a file that is not really our locale
                elif (
                    self.config["fallback_to_default"] is True
                    and i18n_file.locale == self.default_language
                ):
                    i18n_dest_uris[i18n_file.dest_uri] = i18n_file
                    log.debug(f"Use {i18n_file.locale} {i18n_file}")
                else:
                    log.debug(f"Ignore {i18n_file.locale} {i18n_file}")

            # we've seen that file already
            else:
                # override it only if this is our language
                if i18n_file.locale == self.current_language:
                    # users should not add default non suffixed files + suffixed files
                    if i18n_dest_uris[i18n_file.dest_uri].locale == i18n_file.locale:
                        raise Exception(
                            f"Conflicting files for the default language '{self.default_language}': "
                            f"choose either '{i18n_file.src_uri}' or "
                            f"'{i18n_dest_uris[i18n_file.dest_uri].src_uri}' but not both"
                        )
                    i18n_dest_uris[i18n_file.dest_uri] = i18n_file
                    log.debug(f"Use localized {i18n_file.locale} {i18n_file}")
                else:
                    log.debug(f"Ignore {i18n_file.locale} {i18n_file}")

        # theme (and overrides) files
        else:
            if self.is_default_language_build:
                i18n_files.append(file)

    # populate the resulting Files and keep track of all the alternates
    # that will be used by the sitemap.xml template
    for file in i18n_dest_uris.values():
        i18n_files.append(file)

    # keep a reference for alternates reconfiguration
    self.i18n_dest_uris[self.current_language] = i18n_dest_uris

    return i18n_files

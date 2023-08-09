import os
from collections import defaultdict
from pathlib import Path, PurePath
from typing import Optional
from urllib.parse import quote as urlquote

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
    locale_site_dir = current_language if current_language != default_language else ""

    try:
        file_locale = Path(file.name).suffixes.pop(-1).replace(".", "")
        # the file_locale must be a valid language locale code that we check on the
        # configured languages (validated by config) or using the locale regex in case
        # users have localized files but not configured them on the plugin yet
        if file_locale in all_languages or RE_LOCALE.match(file_locale):
            file_dest_path_no_suffix = Path(file_dest_path.parent) / Path(
                file_dest_path.stem
            ).with_suffix("")
            file_dest_path = Path(f"{file_dest_path_no_suffix}{file_dest_path.suffix}")
            # file name suffixed by locale, remove it
            file.name = Path(file.name).stem
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

            # never seen that file?
            if i18n_file.dest_uri not in i18n_dest_uris:
                # best case scenario
                # use the file since its locale is our current build language
                if i18n_file.locale == i18n_plugin.current_language:
                    i18n_dest_uris[i18n_file.dest_uri] = i18n_file
                    log.debug(f"Use {i18n_file.locale} {i18n_file}")
                # if locale is the default language AND default language fallback is enabled
                # we are using a file that is not really our locale
                elif (
                    i18n_plugin.config.fallback_to_default is True
                    and i18n_file.locale == i18n_plugin.default_language
                ) or i18n_file.src_uri.startswith("assets/"):
                    i18n_dest_uris[i18n_file.dest_uri] = i18n_file
                    log.debug(f"Use default {i18n_file.locale} {i18n_file}")
                    if not i18n_file.src_uri.startswith("assets/"):
                        i18n_alternate_dest_uris[i18n_file.dest_uri].append(file)
                else:
                    log.debug(f"Ignore {i18n_file.locale} {i18n_file}")
                    i18n_alternate_dest_uris[i18n_file.dest_uri].append(file)

            # we've seen that file already
            else:
                # override it only if this is our language
                if i18n_file.locale == i18n_plugin.current_language:
                    # users should not add default non suffixed files + suffixed files when
                    # multiple languages are configured
                    if (
                        len(i18n_plugin.all_languages) > 1
                        and i18n_dest_uris[i18n_file.dest_uri].locale == i18n_file.locale
                    ):
                        raise Exception(
                            f"Conflicting files for the default language '{i18n_plugin.default_language}': "
                            f"choose either '{i18n_file.src_uri}' or "
                            f"'{i18n_dest_uris[i18n_file.dest_uri].src_uri}' but not both"
                        )
                    i18n_dest_uris[i18n_file.dest_uri] = i18n_file
                    log.debug(f"Use localized {i18n_file.locale} {i18n_file}")
                else:
                    log.debug(f"Ignore {i18n_file.locale} {i18n_file}")
                    i18n_alternate_dest_uris[i18n_file.dest_uri].append(file)

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

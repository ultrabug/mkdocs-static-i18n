from mkdocs.config.base import load_config
from mkdocs.structure.files import get_files
from mkdocs.structure.nav import get_navigation

STATIC_NAV_DIRECTORY_URLS = {
    "en": {"Home": "/", "Named File": "/topic1/named_file/"},
    "fr": {"Home": "/fr/", "Named File": "/fr/topic1/named_file/"},
}
STATIC_NAV_NO_DIRECTORY_URLS = {
    "en": {"Home": "/index.html", "Named File": "/topic1/named_file.html"},
    "fr": {"Home": "/fr/index.html", "Named File": "/fr/topic1/named_file.html"},
}
TRANSLATED_NAV_DIRECTORY_URLS = {
    "en": {"The Home": "/", "Renamed File": "/topic1/named_file/"},
    "fr": {"Accueil": "/fr/", "Fichier Nommé": "/fr/topic1/named_file/"},
}
TRANSLATED_NAV_NO_DIRECTORY_URLS = {
    "en": {"The Home": "/index.html", "Renamed File": "/topic1/named_file.html"},
    "fr": {"Accueil": "/fr/index.html", "Fichier Nommé": "/fr/topic1/named_file.html"},
}


def test_plugin_static_nav():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        docs_dir="docs_suffix_structure/",
        use_directory_urls=True,
        nav=[
            {"Home": "index.md"},
            {"Topic1": [{"Named File": "topic1/named_file.en.md"}]},
            {"Topic2": "index.en.md"},
            {"External": "https://ultrabug.fr"},
        ],
        plugins={
            "i18n": {
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français"},
                ],
            },
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    for language in i18n_plugin.all_languages:
        config = i18n_plugin.on_config(mkdocs_config)
        #
        i18n_plugin.current_language = language
        #
        files = get_files(config)
        files = i18n_plugin.on_files(files, config)
        nav = get_navigation(files, config)
        nav = i18n_plugin.on_nav(nav, config, files)
        for page in nav.pages:
            assert page.title in STATIC_NAV_DIRECTORY_URLS[language]
            assert page.abs_url == STATIC_NAV_DIRECTORY_URLS[language][page.title]
        assert nav.homepage is not None


def test_plugin_static_nav_no_directory():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        docs_dir="docs_suffix_structure/",
        use_directory_urls=False,
        nav=[
            {"Home": "index.md"},
            {"Topic1": [{"Named File": "topic1/named_file.en.md"}]},
            {"Topic2": "index.en.md"},
            {"External": "https://ultrabug.fr"},
        ],
        plugins={
            "i18n": {
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français"},
                ],
            },
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    for language in i18n_plugin.all_languages:
        config = i18n_plugin.on_config(mkdocs_config)
        #
        i18n_plugin.current_language = language
        #
        files = get_files(config)
        files = i18n_plugin.on_files(files, config)
        nav = get_navigation(files, config)
        nav = i18n_plugin.on_nav(nav, config, files)
        for page in nav.pages:
            assert page.title in STATIC_NAV_NO_DIRECTORY_URLS[language]
            assert page.abs_url == STATIC_NAV_NO_DIRECTORY_URLS[language][page.title]
        assert nav.homepage is not None


def test_plugin_translated_nav():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        docs_dir="docs_suffix_structure/",
        use_directory_urls=True,
        nav=[
            {"Home": "index.md"},
            {"Topic1": [{"Named File": "topic1/named_file.en.md"}]},
            {"Topic2": "index.en.md"},
            {"External": "https://ultrabug.fr"},
        ],
        plugins={
            "i18n": {
                "languages": [
                    {
                        "locale": "en",
                        "default": True,
                        "name": "english",
                        "nav_translations": {
                            "Home": "The Home",
                            "Named File": "Renamed File",
                        },
                    },
                    {
                        "locale": "fr",
                        "name": "français",
                        "nav_translations": {
                            "Home": "Accueil",
                            "Named File": "Fichier Nommé",
                        },
                    },
                ],
            },
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    for language in i18n_plugin.all_languages:
        config = i18n_plugin.on_config(mkdocs_config)
        #
        i18n_plugin.current_language = language
        #
        files = get_files(config)
        files = i18n_plugin.on_files(files, config)
        nav = get_navigation(files, config)
        nav = i18n_plugin.on_nav(nav, config, files)
        for page in nav.pages:
            assert page.title in TRANSLATED_NAV_DIRECTORY_URLS[language]
            assert page.abs_url == TRANSLATED_NAV_DIRECTORY_URLS[language][page.title]
        assert nav.homepage is not None


def test_plugin_translated_nav_no_directory():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        docs_dir="docs_suffix_structure/",
        use_directory_urls=False,
        nav=[
            {"Home": "index.md"},
            {"Topic1": [{"Named File": "topic1/named_file.en.md"}]},
            {"Topic2": "index.en.md"},
            {"External": "https://ultrabug.fr"},
        ],
        plugins={
            "i18n": {
                "languages": [
                    {
                        "locale": "en",
                        "default": True,
                        "name": "english",
                        "nav_translations": {
                            "Home": "The Home",
                            "Named File": "Renamed File",
                        },
                    },
                    {
                        "locale": "fr",
                        "name": "français",
                        "nav_translations": {
                            "Home": "Accueil",
                            "Named File": "Fichier Nommé",
                        },
                    },
                ],
            },
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    for language in i18n_plugin.all_languages:
        config = i18n_plugin.on_config(mkdocs_config)
        #
        i18n_plugin.current_language = language
        #
        files = get_files(config)
        files = i18n_plugin.on_files(files, config)
        nav = get_navigation(files, config)
        nav = i18n_plugin.on_nav(nav, config, files)
        for page in nav.pages:
            assert page.title in TRANSLATED_NAV_NO_DIRECTORY_URLS[language]
            assert (
                page.abs_url == TRANSLATED_NAV_NO_DIRECTORY_URLS[language][page.title]
            )
        assert nav.homepage is not None

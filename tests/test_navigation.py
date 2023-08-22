import pytest
from mkdocs.config.base import load_config
from mkdocs.structure.files import get_files
from mkdocs.structure.nav import get_navigation

STATIC_NAV_DIRECTORY_URLS = {
    "en": {"Home": "/", "Named File": "/topic1/named_file/", "Topic2": "/topic2/"},
    "fr": {"Home": "/fr/", "Named File": "/fr/topic1/named_file/", "Topic2": "/fr/topic2/"},
}
STATIC_NAV_NO_DIRECTORY_URLS = {
    "en": {
        "Home": "/index.html",
        "Named File": "/topic1/named_file.html",
        "Topic2": "/topic2/index.html",
    },
    "fr": {
        "Home": "/fr/index.html",
        "Named File": "/fr/topic1/named_file.html",
        "Topic2": "/fr/topic2/index.html",
    },
}
TRANSLATED_NAV_DIRECTORY_URLS = {
    "en": {"The Home": "/", "Renamed File": "/topic1/named_file/", "Topic2": "/topic2/"},
    "fr": {"Accueil": "/fr/", "Fichier Nommé": "/fr/topic1/named_file/", "Topic2": "/fr/topic2/"},
}
TRANSLATED_NAV_NO_DIRECTORY_URLS = {
    "en": {
        "The Home": "/index.html",
        "Renamed File": "/topic1/named_file.html",
        "Topic2": "/topic2/index.html",
    },
    "fr": {
        "Accueil": "/fr/index.html",
        "Fichier Nommé": "/fr/topic1/named_file.html",
        "Topic2": "/fr/topic2/index.html",
    },
}


@pytest.mark.parametrize(
    "plugin_config,use_directory_urls,control_data",
    [
        (
            {
                "docs_structure": "suffix",
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français"},
                ],
            },
            True,
            STATIC_NAV_DIRECTORY_URLS,
        ),
        (
            {
                "docs_structure": "suffix",
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français"},
                ],
            },
            False,
            STATIC_NAV_NO_DIRECTORY_URLS,
        ),
        (
            {
                "docs_structure": "suffix",
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
            True,
            TRANSLATED_NAV_DIRECTORY_URLS,
        ),
        (
            {
                "docs_structure": "suffix",
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
            False,
            TRANSLATED_NAV_NO_DIRECTORY_URLS,
        ),
        (
            {
                "docs_structure": "folder",
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français"},
                ],
            },
            True,
            STATIC_NAV_DIRECTORY_URLS,
        ),
        (
            {
                "docs_structure": "folder",
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français"},
                ],
            },
            False,
            STATIC_NAV_NO_DIRECTORY_URLS,
        ),
        (
            {
                "docs_structure": "folder",
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
            True,
            TRANSLATED_NAV_DIRECTORY_URLS,
        ),
        (
            {
                "docs_structure": "folder",
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
            False,
            TRANSLATED_NAV_NO_DIRECTORY_URLS,
        ),
    ],
)
def test_plugin_navigation(plugin_config, use_directory_urls, control_data):
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        docs_dir=f"docs_{plugin_config['docs_structure']}_structure/",
        use_directory_urls=use_directory_urls,
        nav=[
            {"Home": "index.md"},
            {"Topic1": [{"Named File": "topic1/named_file.md"}]},
            {"Topic2": "topic2/README.md"},
            {"External": "https://ultrabug.fr"},
        ],
        plugins={
            "i18n": plugin_config,
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
        assert len(mkdocs_config.nav) == len(nav.pages) + 1  # +1 for external link
        for page in nav.pages:
            assert page.title in control_data[language]
            assert page.abs_url == control_data[language][page.title]
        assert nav.homepage is not None

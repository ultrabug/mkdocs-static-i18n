import pytest
from mkdocs.config.base import load_config
from mkdocs.exceptions import Abort


def test_plugin_languages_no_default():
    with pytest.raises(Abort):
        load_config(
            "tests/mkdocs.yml",
            theme={"name": "mkdocs"},
            use_directory_urls=True,
            docs_dir="docs_suffix_structure/",
            plugins={
                "i18n": {
                    "languages": [
                        {
                            "locale": "en",
                            "name": "english",
                            "default": False,
                        },
                    ],
                },
            },
        )


def test_plugin_languages_no_build():
    with pytest.raises(Abort):
        load_config(
            "tests/mkdocs.yml",
            theme={"name": "mkdocs"},
            use_directory_urls=True,
            docs_dir="docs_suffix_structure/",
            plugins={
                "i18n": {
                    "languages": [
                        {
                            "locale": "en",
                            "name": "english",
                            "default": True,
                            "build": False,
                        },
                        {"locale": "fr", "name": "français", "build": False},
                    ],
                },
            },
        )


def test_plugin_languages_dual_lang():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
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
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == [
        {
            "locale": "en",
            "name": "english",
            "link": "/",
            "fixed_link": None,
            "build": True,
            "default": True,
            "nav": None,
            "nav_translations": None,
            "theme": None,
            "site_name": None,
            "copyright": None,
            "extra": None,
            "site_author": None,
            "site_description": None,
            "site_url": None,
        },
        {
            "locale": "fr",
            "name": "français",
            "link": "/fr/",
            "fixed_link": None,
            "build": True,
            "default": False,
            "nav": None,
            "nav_translations": None,
            "theme": None,
            "site_name": None,
            "copyright": None,
            "extra": None,
            "site_author": None,
            "site_description": None,
            "site_url": None,
        },
    ]


def test_plugin_languages_one_lang():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "i18n": {
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                ],
            },
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == [
        {
            "locale": "en",
            "name": "english",
            "link": "/",
            "fixed_link": None,
            "build": True,
            "default": True,
            "nav": None,
            "nav_translations": None,
            "theme": None,
            "site_name": None,
            "copyright": None,
            "extra": None,
            "site_author": None,
            "site_description": None,
            "site_url": None,
        },
    ]

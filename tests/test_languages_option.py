import pytest
from mkdocs.config.base import load_config
from mkdocs.exceptions import Abort


def test_plugin_languages_no_default():
    with pytest.raises(Abort):
        load_config(
            "tests/mkdocs.yml",
            theme={"name": "mkdocs"},
            use_directory_urls=True,
            docs_dir="docs_suffix_structure_one_language/",
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
            docs_dir="docs_suffix_structure_two_languages/",
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
        docs_dir="docs_suffix_structure_two_languages/",
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
        docs_dir="docs_suffix_structure_one_language/",
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


def test_plugin_languages_null_no_fixed_link():
    with pytest.raises(Abort):
        load_config(
            "tests/mkdocs.yml",
            theme={"name": "mkdocs"},
            use_directory_urls=True,
            docs_dir="docs_suffix_structure_two_languages/",
            plugins={
                "i18n": {
                    "languages": [
                        {
                            "locale": "en",
                            "name": "english",
                            "default": True,
                        },
                        {"locale": "fr", "name": "français"},
                        {"locale": "null", "name": "help"},
                    ],
                },
            },
        )


def test_plugin_languages_dual_lang_with_null():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure_two_languages/",
        plugins={
            "i18n": {
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français"},
                    {"locale": "null", "name": "help", "fixed_link": "https://ultrabug.fr"},
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
        {
            "locale": "null",
            "name": "help",
            "link": "/null/",
            "fixed_link": "https://ultrabug.fr",
            "build": False,
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


def test_plugin_build_only_locale():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "material"},
        docs_dir="docs_suffix_structure_two_languages/",
        plugins={
            "i18n": {
                "build_only_locale": "fr",
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                        "build": True,
                    },
                    {
                        "locale": "fr", 
                        "name": "français",
                        "default": False,
                        "build": False, 
                    },
                ],
            }
        },
    )
    
    english = mkdocs_config["plugins"]["i18n"].config.languages[0]
    french = mkdocs_config["plugins"]["i18n"].config.languages[1]

    assert english["default"] == False
    assert english["build"] == False
    assert french["default"] == True
    assert french["build"] == True


def test_plugin_build_only_locale_abort():
    with pytest.raises(Abort):
        load_config(
            "tests/mkdocs.yml",
            theme={"name": "material"},
            docs_dir="docs_suffix_structure_two_languages/",
            plugins={
                "i18n": {
                    "build_only_locale": "zh",
                    "languages": [
                        {
                            "locale": "en",
                            "name": "english",
                            "default": True,
                            "build": True,
                        },
                        {
                            "locale": "fr", 
                            "name": "français",
                            "default": False,
                            "build": False, 
                        },
                    ],
                }
            },
        )

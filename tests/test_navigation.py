from copy import copy
from pathlib import Path

from mkdocs.commands.build import build
from mkdocs.config.base import load_config
from mkdocs.structure.files import get_files
from mkdocs.structure.nav import get_navigation

EN_STATIC_NAV = [
    {"Home": "index.md"},
    {"Topic1": [{"Named File": str(Path("topic1/named_file.en.md"))}]},
    {"Topic2": "index.en.md"},
    {"External": "https://ultrabug.fr"},
]


FR_STATIC_NAV = [
    {"Home": "index.fr.md"},
    {"Topic1": [{"Named File": str(Path("topic1/named_file.fr.md"))}]},
    {"Topic2": "index.fr.md"},
    {"External": "https://ultrabug.fr"},
]


EN_TRANSLATED_NAV = [
    {"The Home": "index.md"},
    {"Translated1": [{"Renamed File": str(Path("topic1/named_file.en.md"))}]},
    {"Translated2": "index.en.md"},
    {"External": "https://ultrabug.fr"},
]

FR_TRANSLATED_NAV = [
    {"Accueil": "index.fr.md"},
    {"Sujet1": [{"Fichier Nommé": str(Path("topic1/named_file.fr.md"))}]},
    {"Sujet2": "index.fr.md"},
    {"External": "https://ultrabug.fr"},
]


def test_plugin_static_nav(config_plugin_static_nav):
    config = config_plugin_static_nav
    i18n_plugin = config["plugins"]["i18n"]
    #
    files = get_files(config)
    config = i18n_plugin.on_config(config)
    files = i18n_plugin.on_files(files, config)
    nav = get_navigation(files, config)
    nav = i18n_plugin.on_nav(nav, config, files)
    env = config.theme.get_env()
    env = i18n_plugin.on_env(env, config, files)
    i18n_plugin.on_post_build(config)
    #
    assert i18n_plugin.i18n_configs["en"]["nav"] == EN_STATIC_NAV
    assert i18n_plugin.i18n_configs["fr"]["nav"] == FR_STATIC_NAV


def test_plugin_translated_nav(config_plugin_translated_nav):
    config = config_plugin_translated_nav
    i18n_plugin = config["plugins"]["i18n"]
    #
    files = get_files(config)
    config = i18n_plugin.on_config(config)
    files = i18n_plugin.on_files(files, config)
    nav = get_navigation(files, config)
    nav = i18n_plugin.on_nav(nav, config, files)
    env = config.theme.get_env()
    env = i18n_plugin.on_env(env, config, files)
    i18n_plugin.on_post_build(config)
    #
    fr_config = copy(i18n_plugin.i18n_configs["fr"])
    fr_config["nav"] = FR_TRANSLATED_NAV
    fr_nav = get_navigation(i18n_plugin.i18n_files["fr"], fr_config)
    assert i18n_plugin.i18n_navs["fr"].__repr__() == fr_nav.__repr__()
    #
    en_config = copy(i18n_plugin.i18n_configs["en"])
    en_config["nav"] = EN_TRANSLATED_NAV
    en_nav = get_navigation(i18n_plugin.i18n_files["en"], en_config)
    assert i18n_plugin.i18n_navs["en"].__repr__() == en_nav.__repr__()


def test_homepage_detection_folder_no_use_directory():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_folder_structure/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "search": {},
            "i18n": {
                "default_language_only": True,
                "default_language": "en",
                "docs_structure": "folder",
                "languages": {"fr": "français", "en": "english"},
            },
        },
    )
    build(mkdocs_config)
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    for lang in i18n_plugin.config["languages"]:
        assert i18n_plugin.i18n_navs[lang].homepage is not None


def test_homepage_detection_folder_use_directory():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_folder_structure/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "search": {},
            "i18n": {
                "default_language_only": True,
                "default_language": "en",
                "docs_structure": "folder",
                "languages": {"fr": "français", "en": "english"},
            },
        },
    )
    build(mkdocs_config)
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    for lang in i18n_plugin.config["languages"]:
        assert i18n_plugin.i18n_navs[lang].homepage is not None


def test_homepage_detection_suffix_no_use_directory():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_suffix_structure/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "search": {},
            "i18n": {
                "default_language_only": True,
                "default_language": "en",
                "docs_structure": "suffix",
                "languages": {"fr": "français", "en": "english"},
            },
        },
    )
    build(mkdocs_config)
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    for lang in i18n_plugin.config["languages"]:
        assert i18n_plugin.i18n_navs[lang].homepage is not None


def test_homepage_detection_suffix_use_directory():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "search": {},
            "i18n": {
                "default_language_only": True,
                "default_language": "en",
                "docs_structure": "suffix",
                "languages": {"fr": "français", "en": "english"},
            },
        },
    )
    build(mkdocs_config)
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    for lang in i18n_plugin.config["languages"]:
        assert i18n_plugin.i18n_navs[lang].homepage is not None


def test_plugin_translated_default_nav_suffix():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_suffix_structure/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "search": {},
            "i18n": {
                "default_language_only": True,
                "default_language": "fr",
                "docs_structure": "suffix",
                "languages": {"fr": "français", "en": "english"},
                "nav_translations": {
                    "en": {
                        "Home": "EN Home",
                        "Named File": "EN Named File",
                        "Topic1": "EN Topic1",
                        "Topic2": "EN Topic2",
                    },
                    "fr": {
                        "Home": "Accueil",
                        "Named File": "Fichier Nommé",
                        "Topic1": "Sujet1",
                        "Topic2": "Sujet2",
                    },
                },
            },
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    files = get_files(mkdocs_config)
    config = i18n_plugin.on_config(mkdocs_config)
    files = i18n_plugin.on_files(files, config)
    nav = get_navigation(files, config)
    nav = i18n_plugin.on_nav(nav, config, files)
    i18n_plugin.on_post_build(config)
    #
    expected_titles = set(
        mkdocs_config["plugins"]["i18n"].config["nav_translations"]["fr"].values()
    )

    def assert_title(item, expected_titles):
        if item.title:
            assert item.title in expected_titles

    for item in nav:
        if item.title:
            assert_title(item, expected_titles)
        if item.children:
            for item in item.children:
                assert_title(item, expected_titles)


def test_plugin_translated_default_nav_folder():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_folder_structure/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "search": {},
            "i18n": {
                "default_language_only": True,
                "default_language": "fr",
                "docs_structure": "folder",
                "languages": {"fr": "français", "en": "english"},
                "nav_translations": {
                    "en": {
                        "Home": "EN Home",
                        "Named File": "EN Named File",
                        "Topic1": "EN Topic1",
                        "Topic2": "EN Topic2",
                    },
                    "fr": {
                        "Home": "Accueil",
                        "Named File": "Fichier Nommé",
                        "Topic1": "Sujet1",
                        "Topic2": "Sujet2",
                    },
                },
            },
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    files = get_files(mkdocs_config)
    config = i18n_plugin.on_config(mkdocs_config)
    files = i18n_plugin.on_files(files, config)
    nav = get_navigation(files, config)
    nav = i18n_plugin.on_nav(nav, config, files)
    i18n_plugin.on_post_build(config)
    #
    expected_titles = set(
        mkdocs_config["plugins"]["i18n"].config["nav_translations"]["fr"].values()
    )

    def assert_title(item, expected_titles):
        if item.title:
            assert item.title in expected_titles

    for item in nav:
        if item.title:
            assert_title(item, expected_titles)
        if item.children:
            for item in item.children:
                assert_title(item, expected_titles)

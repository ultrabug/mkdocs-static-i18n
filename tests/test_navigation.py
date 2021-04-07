from pathlib import Path

from mkdocs.structure.files import get_files
from mkdocs.structure.nav import get_navigation

MAIN_STATIC_NAV = [
    {"Home": "index.md"},
    {"Topic1": [{"Named File": str(Path("topic1/named_file.en.md"))}]},
    {"Topic2": "index.en.md"},
]

EN_STATIC_NAV = [
    {"Home": "index.md"},
    {"Topic1": [{"Named File": str(Path("topic1/named_file.en.md"))}]},
    {"Topic2": "index.en.md"},
]


FR_STATIC_NAV = [
    {"Home": "index.fr.md"},
    {"Topic1": [{"Named File": str(Path("topic1/named_file.fr.md"))}]},
    {"Topic2": "index.fr.md"},
]


def test_plugin_static_nav(config_plugin_static_nav):
    config = config_plugin_static_nav
    i18n_plugin = config["plugins"]["i18n"]
    #
    files = get_files(config)
    i18n_files = i18n_plugin.on_files(files, config)
    nav = get_navigation(i18n_files, config)
    i18n_plugin.on_nav(nav, config, i18n_files)
    #
    assert MAIN_STATIC_NAV == EN_STATIC_NAV
    assert MAIN_STATIC_NAV == config["nav"]
    assert i18n_plugin.i18n_configs["en"]["nav"] == EN_STATIC_NAV
    assert i18n_plugin.i18n_configs["fr"]["nav"] == FR_STATIC_NAV

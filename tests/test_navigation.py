from copy import deepcopy
from pathlib import Path

from mkdocs.structure.files import get_files
from mkdocs.structure.nav import get_navigation

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


FR_TRANSLATED_NAV = [
    {"Accueil": "index.fr.md"},
    {"Sujet1": [{"Fichier Nommé": str(Path("topic1/named_file.fr.md"))}]},
    {"Sujet2": "index.fr.md"},
]


def test_plugin_static_nav(config_plugin_static_nav):
    config = config_plugin_static_nav
    i18n_plugin = config["plugins"]["i18n"]
    #
    files = get_files(config)
    i18n_plugin.on_config(config)
    i18n_plugin.on_files(files, config)
    i18n_plugin.on_post_build(config)
    #
    assert i18n_plugin.i18n_configs["en"]["nav"] == EN_STATIC_NAV
    assert i18n_plugin.i18n_configs["fr"]["nav"] == FR_STATIC_NAV


def test_plugin_translated_nav(config_plugin_translated_nav):
    config = config_plugin_translated_nav
    i18n_plugin = config["plugins"]["i18n"]
    #
    files = get_files(config)
    i18n_plugin.on_config(config)
    i18n_plugin.on_files(files, config)
    i18n_plugin.on_post_build(config)
    #
    fr_config = deepcopy(i18n_plugin.i18n_configs["fr"])
    fr_config["nav"] = FR_TRANSLATED_NAV
    fr_nav = get_navigation(i18n_plugin.i18n_files["fr"], fr_config)
    assert i18n_plugin.i18n_navs["fr"].__repr__() == fr_nav.__repr__()
    #
    en_config = deepcopy(i18n_plugin.i18n_configs["en"])
    en_config["nav"] = EN_STATIC_NAV
    en_nav = get_navigation(i18n_plugin.i18n_files["en"], en_config)
    assert i18n_plugin.i18n_navs["en"].__repr__() == en_nav.__repr__()

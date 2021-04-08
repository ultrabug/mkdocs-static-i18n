from pathlib import Path

from mkdocs.structure.files import get_files

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
    i18n_plugin.on_files(files, config)
    i18n_plugin.on_post_build(config)
    #
    assert i18n_plugin.i18n_configs["en"]["nav"] == EN_STATIC_NAV
    assert i18n_plugin.i18n_configs["fr"]["nav"] == FR_STATIC_NAV

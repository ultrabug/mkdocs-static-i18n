from mkdocs.config.base import load_config

from mkdocs_static_i18n.plugin import I18n

ALTERNATE_USE_DIRECTORY_URLS = [
    {"name": "english", "link": "./index.html", "lang": "en"},
    {"name": "français", "link": "./fr/index.html", "lang": "fr"},
]

ALTERNATE_NO_USE_DIRECTORY_URLS = [
    {"name": "english", "link": "./", "lang": "en"},
    {"name": "français", "link": "./fr/", "lang": "fr"},
]


def test_plugin_language_selector_use_directory_urls():
    plugin = I18n()
    plugin.load_config(
        {"default_language": "en", "languages": {"fr": "français", "en": "english"}}
    )
    config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="../docs/",
        extra_javascript=[],
    )
    result = plugin.on_config(config, force=True)
    assert result["extra"]["alternate"] == ALTERNATE_USE_DIRECTORY_URLS


def test_plugin_language_selector_no_use_directory_urls():
    plugin = I18n()
    plugin.load_config(
        {"default_language": "en", "languages": {"fr": "français", "en": "english"}}
    )
    config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="../docs/",
        extra_javascript=[],
    )
    result = plugin.on_config(config, force=True)
    assert result["extra"]["alternate"] == ALTERNATE_NO_USE_DIRECTORY_URLS

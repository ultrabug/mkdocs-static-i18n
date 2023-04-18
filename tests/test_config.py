from mkdocs.config.base import load_config

from mkdocs_static_i18n.plugin import I18n


def test_plugin_single_language_en():
    plugin = I18n()
    plugin.load_config({"languages": [{"locale": "en", "name": "english", "default": True}]})
    config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
    )
    result = plugin.on_config(config)
    assert str(result["theme"]["locale"]) == "en"


def test_plugin_single_language_fr():
    plugin = I18n()
    plugin.load_config({"languages": [{"locale": "fr", "name": "français", "default": True}]})
    config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
    )
    result = plugin.on_config(config)
    assert str(result["theme"]["locale"]) == "fr"


def test_plugin_theme_sitemap():
    plugin = I18n()
    plugin.load_config({"languages": [{"locale": "fr", "name": "français", "default": True}]})
    config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
    )
    result = plugin.on_config(config)
    assert result["theme"].dirs[0].endswith("custom_i18n_sitemap")

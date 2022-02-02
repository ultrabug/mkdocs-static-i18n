from mkdocs.config.base import load_config

from mkdocs_static_i18n.plugin import I18n


def test_plugin_single_language_en():
    plugin = I18n()
    plugin.load_config({"default_language": "en", "languages": {"en": "english"}})
    config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="../docs/",
        site_url="http://localhost",
        extra_javascript=[],
    )
    result = plugin.on_config(config, force=True)
    assert str(result["theme"]["locale"]) == "en"


def test_plugin_single_language_fr():
    plugin = I18n()
    plugin.load_config({"default_language": "fr", "languages": {"fr": "français"}})
    config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="../docs/",
        site_url="http://localhost",
        extra_javascript=[],
    )
    result = plugin.on_config(config, force=True)
    assert str(result["theme"]["locale"]) == "fr"


def test_plugin_theme_sitemap():
    plugin = I18n()
    plugin.load_config({"default_language": "fr", "languages": {"fr": "français"}})
    config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="../docs/",
        site_url="http://localhost",
        extra_javascript=[],
    )
    result = plugin.on_config(config, force=True)
    assert result["theme"].dirs[0].endswith("custom_i18n_sitemap")

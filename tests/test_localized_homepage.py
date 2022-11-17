from mkdocs.config.base import load_config

from mkdocs_static_i18n.plugin import I18n

HOMEPAGE = {"de": "https://ulricusr.github.io/de", "en": "https://ulricusr.github.io/en"}

def test_plugin_localized_homepage():
    plugin = I18n()
    plugin.load_config({
        "default_language": "en",
        "languages": {
            "en": {
                "name": "English",
                "homepage": HOMEPAGE["en"]
            },
            "de": {
                "name": "Deutsch",
                "homepage": HOMEPAGE["de"]
            }
        }
    })
    config = load_config(
        "tests/mkdocs_base.yml",
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        site_url="http://localhost",
        extra_javascript=[],
    )
    result = plugin.on_config(config, force=True)
    assert str(result["extra"]["homepage"]) == HOMEPAGE[plugin.default_language]
    for language in plugin.config["languages"]:
        assert str(plugin.i18n_configs[language]["extra"]["homepage"]) == HOMEPAGE[language]

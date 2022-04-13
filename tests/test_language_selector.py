from mkdocs.config.base import load_config

ALTERNATE_NO_USE_DIRECTORY_URLS = [
    {"name": "english", "link": "./index.html", "lang": "en"},
    {"name": "français", "link": "./fr/index.html", "lang": "fr"},
]

ALTERNATE_USE_DIRECTORY_URLS = [
    {"name": "english", "link": "./", "lang": "en"},
    {"name": "français", "link": "./fr/", "lang": "fr"},
]


def test_plugin_language_selector_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "i18n": {
                "default_language": "en",
                "languages": {"fr": "français", "en": "english"},
            }
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    result = i18n_plugin.on_config(mkdocs_config, force=True)
    assert result["extra"]["alternate"] == ALTERNATE_USE_DIRECTORY_URLS


def test_plugin_language_selector_no_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_suffix_structure/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "i18n": {
                "default_language": "en",
                "languages": {"fr": "français", "en": "english"},
            }
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    result = i18n_plugin.on_config(mkdocs_config, force=True)
    assert result["extra"]["alternate"] == ALTERNATE_NO_USE_DIRECTORY_URLS


def test_plugin_language_selector_single_default_language():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={"i18n": {"default_language": "fr", "languages": {"fr": "français"}}},
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    result = i18n_plugin.on_config(mkdocs_config, force=True)
    assert result["extra"] == {}


def test_plugin_language_selector_use_directory_urls_default():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "i18n": {
                "default_language": "en",
                "languages": {
                    "default": {"name": "default_english"},
                    "fr": "français",
                    "en": "english",
                },
            }
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    result = i18n_plugin.on_config(mkdocs_config, force=True)
    assert result["extra"]["alternate"] == [
        {"name": "default_english", "link": "./", "lang": "en"},
        {"name": "français", "link": "./fr/", "lang": "fr"},
        {"name": "english", "link": "./en/", "lang": "en"},
    ]

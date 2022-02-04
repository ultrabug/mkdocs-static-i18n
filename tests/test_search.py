from mkdocs.commands.build import build
from mkdocs.config.base import load_config


def test_search_add_lang():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="../docs/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "search": {},
            "i18n": {
                "default_language": "en",
                "languages": {"fr": "français", "en": "english"},
            },
        },
    )
    build(mkdocs_config)
    search_plugin = mkdocs_config["plugins"]["search"]
    assert search_plugin.config["lang"] == ["en", "fr"]


def test_search_entries():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="../docs/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "search": {},
            "i18n": {
                "default_language": "en",
                "languages": {
                    "fr": {"name": "français", "link": "./fr/", "build": True}
                },
            },
        },
    )
    build(mkdocs_config)
    search_plugin = mkdocs_config["plugins"]["search"]
    assert len(search_plugin.search_index._entries) == 30


def test_search_entries_no_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="../docs/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "search": {},
            "i18n": {
                "default_language": "en",
                "languages": {"fr": "français"},
            },
        },
    )
    build(mkdocs_config)
    search_plugin = mkdocs_config["plugins"]["search"]
    assert len(search_plugin.search_index._entries) == 30


def test_search_deduplicate_entries():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="../docs/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "search": {},
            "i18n": {
                "default_language": "en",
                "languages": {"fr": "français", "en": "english"},
            },
        },
    )
    build(mkdocs_config)
    search_plugin = mkdocs_config["plugins"]["search"]
    assert len(search_plugin.search_index._entries) == 30


def test_search_deduplicate_entries_no_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="../docs/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "search": {},
            "i18n": {
                "default_language": "en",
                "languages": {"fr": "français", "en": "english"},
            },
        },
    )
    build(mkdocs_config)
    search_plugin = mkdocs_config["plugins"]["search"]
    assert len(search_plugin.search_index._entries) == 30

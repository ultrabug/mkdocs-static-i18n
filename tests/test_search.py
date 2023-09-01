from mkdocs.commands.build import build
from mkdocs.config.base import load_config


def test_search_entries():
    for theme in ["mkdocs", "material"]:
        mkdocs_config = load_config(
            "tests/mkdocs.yml",
            theme={"name": theme},
            use_directory_urls=True,
            docs_dir="docs_suffix_structure/",
            plugins={
                "search": {},
                "i18n": {
                    "languages": [
                        {
                            "locale": "en",
                            "name": "english",
                            "default": True,
                        },
                        {"locale": "fr", "name": "français"},
                    ],
                },
            },
        )
        if theme == "material":
            mkdocs_config["plugins"]["material/search"].on_startup(command=None, dirty=False)
        build(mkdocs_config)
        if theme == "mkdocs":
            search_plugin = mkdocs_config["plugins"]["search"]
            assert len(search_plugin.search_index._entries) == 34
        else:
            search_plugin = mkdocs_config["plugins"]["material/search"]
            assert len(search_plugin.search_index.entries) == 26


def test_search_entries_no_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_suffix_structure/",
        plugins={
            "search": {},
            "i18n": {
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français"},
                ],
            },
        },
    )
    build(mkdocs_config)
    search_plugin = mkdocs_config["plugins"]["search"]
    assert len(search_plugin.search_index._entries) == 34


def test_search_entries_no_reconfigure():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "search": {},
            "i18n": {
                "reconfigure_search": False,
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français"},
                ],
            },
        },
    )
    build(mkdocs_config)
    search_plugin = mkdocs_config["plugins"]["search"]
    assert len(search_plugin.search_index._entries) == 36


def test_search_add_lang():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "search": {},
            "i18n": {
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français"},
                ],
            },
        },
    )
    build(mkdocs_config)
    search_plugin = mkdocs_config["plugins"]["search"]
    assert search_plugin.config["lang"] == ["en", "fr"]


def test_search_add_missing_lang():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "search": {
                "lang": ["en"],
            },
            "i18n": {
                "reconfigure_search": True,
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français"},
                ],
            },
        },
    )
    build(mkdocs_config)
    search_plugin = mkdocs_config["plugins"]["search"]
    assert search_plugin.config["lang"] == ["en", "fr"]


def test_search_no_add_lang():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "search": {
                "lang": ["en"],
            },
            "i18n": {
                "reconfigure_search": False,
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français"},
                ],
            },
        },
    )
    build(mkdocs_config)
    search_plugin = mkdocs_config["plugins"]["search"]
    assert search_plugin.config["lang"] == ["en"]

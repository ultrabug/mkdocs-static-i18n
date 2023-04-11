from mkdocs.config.base import load_config


def test_plugin_languages_backward_compat_1():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "i18n": {
                "languages": {
                    "en": {"name": "english", "default": True},
                    "fr": {"name": "français"},
                },
            },
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "english",
            "link": "./",
            "fixed_link": None,
            "build": True,
            "default": True,
        },
        "fr": {
            "name": "français",
            "link": "./fr/",
            "fixed_link": None,
            "build": True,
            "default": False,
        },
    }


def test_plugin_languages_backward_compat_2():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "i18n": {
                "languages": {
                    "en": {"name": "english", "default": True},
                },
            },
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "english",
            "link": "./",
            "fixed_link": None,
            "build": True,
            "default": True,
        },
    }


def test_plugin_languages_backward_compat_3():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "i18n": {
                "languages": {
                    "en": {"name": "english", "default": True, "build": False},
                    "fr": {"name": "français"},
                },
            },
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "english",
            "link": "./",
            "fixed_link": None,
            "build": False,
            "default": True,
        },
        "fr": {
            "name": "français",
            "link": "./fr/",
            "fixed_link": None,
            "build": True,
            "default": False,
        },
    }

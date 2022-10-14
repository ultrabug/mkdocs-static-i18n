from mkdocs.config.base import load_config


def test_plugin_languages_backward_compat_1():
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
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "english",
            "link": "./en/",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
        "fr": {
            "name": "français",
            "link": "./fr/",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
    }


def test_plugin_languages_backward_compat_2():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={"i18n": {"default_language": "en", "languages": {"en": "english"}}},
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "english",
            "link": "./en/",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
    }


def test_plugin_languages_backward_compat_3():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={"i18n": {"default_language": "en", "languages": {"fr": "français"}}},
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "en",
            "link": "./",
            "fixed_link": None,
            "build": False,
            "site_name": "MkDocs static i18n plugin tests",
        },
        "fr": {
            "name": "français",
            "link": "./fr/",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
    }


def test_plugin_languages_backward_compat_4():
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
                "languages": {"default": {"name": "english_default"}, "fr": "français"},
            }
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "english_default",
            "link": "./",
            "fixed_link": None,
            "build": False,
            "site_name": "MkDocs static i18n plugin tests",
        },
        "fr": {
            "name": "français",
            "link": "./fr/",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
    }


def test_plugin_languages_backward_compat_5():
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
                    "default": {"name": "english_default"},
                    "fr": "français",
                    "en": {
                        "name": "english",
                        "build": True,
                        "site_name": "English site name",
                    },
                },
            }
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "english",
            "link": "./en/",
            "fixed_link": None,
            "build": True,
            "site_name": "English site name",
        },
        "fr": {
            "name": "français",
            "link": "./fr/",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
    }


def test_plugin_languages_backward_compat_6():
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
                    "default": {"name": "english_default"},
                    "fr": {"name": "français", "link": "/fr"},
                    "en": {
                        "name": "english",
                        "build": False,
                        "site_name": "MkDocs static i18n plugin tests",
                    },
                },
            }
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "english",
            "link": "./en/",
            "fixed_link": None,
            "build": False,
            "site_name": "MkDocs static i18n plugin tests",
        },
        "fr": {
            "name": "français",
            "link": "/fr",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
    }


def test_plugin_languages_backward_compat_7():
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
                "languages": {"fr": {"name": "français"}, "en": {"name": "english"}},
            }
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "english",
            "link": "./en/",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
        "fr": {
            "name": "français",
            "link": "./fr/",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
    }


def test_plugin_languages_backward_compat_8():
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
                    "default": {"name": "english_default"},
                    "fr": "français",
                    "en": {"name": "english", "build": True},
                },
            }
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "english",
            "link": "./en/",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
        "fr": {
            "name": "français",
            "link": "./fr/",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
    }


def test_plugin_languages_backward_compat_9():
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
                    "default": {"name": "english_default"},
                    "fr": "français",
                    "en": {"name": "english", "build": False},
                },
            }
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "english",
            "link": "./en/",
            "fixed_link": None,
            "build": False,
            "site_name": "MkDocs static i18n plugin tests",
        },
        "fr": {
            "name": "français",
            "link": "./fr/",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
    }


def test_plugin_languages_backward_compat_10():
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
                    "default": {"name": "english_default", "build": True},
                    "fr": "français",
                },
            }
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "english_default",
            "link": "./",
            "fixed_link": None,
            "build": False,
            "site_name": "MkDocs static i18n plugin tests",
        },
        "fr": {
            "name": "français",
            "link": "./fr/",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
    }


def test_plugin_languages_backward_compat_11():
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
                    "default": {"build": True},
                    "fr": "français",
                },
            }
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "en",
            "link": "./",
            "fixed_link": None,
            "build": False,
            "site_name": "MkDocs static i18n plugin tests",
        },
        "fr": {
            "name": "français",
            "link": "./fr/",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
    }


def test_plugin_languages_backward_compat_12():
    mkdocs_config = load_config(
        "tests/mkdocs_base.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        site_url="http://localhost",
        extra_javascript=[],
        plugins={
            "i18n": {
                "default_language": "fr",
                "languages": {
                    "default": {"name": "french_default"},
                },
            }
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.config["languages"] == {
        "fr": {
            "name": "french_default",
            "link": "./",
            "fixed_link": None,
            "build": True,
            "site_name": "MkDocs static i18n plugin tests",
        },
    }


def test_plugin_languages_backward_compat_13():
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
                    "default": {
                        "name": "english_default",
                        "site_name": "Default site name",
                    },
                    "fr": {"name": "français", "site_name": "Site en Français"},
                    "en": {
                        "name": "english",
                        "build": True,
                        "site_name": "English site name",
                    },
                },
            }
        },
    )
    i18n_plugin = mkdocs_config["plugins"]["i18n"]
    i18n_plugin.on_config(mkdocs_config)
    assert i18n_plugin.default_language_options["site_name"] == "Default site name"
    assert i18n_plugin.config["languages"] == {
        "en": {
            "name": "english",
            "link": "./en/",
            "fixed_link": None,
            "build": True,
            "site_name": "English site name",
        },
        "fr": {
            "name": "français",
            "link": "./fr/",
            "fixed_link": None,
            "build": True,
            "site_name": "Site en Français",
        },
    }

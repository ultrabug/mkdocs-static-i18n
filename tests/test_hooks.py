from mkdocs.commands.build import build
from mkdocs.config.base import load_config


def test_hooks_working():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "i18n": {
                "languages": [
                    {"locale": "en", "name": "english", "default": True},
                    {"locale": "fr", "name": "français"},
                ],
            },
        },
        hooks=["hooks.py"],
    )
    build(mkdocs_config)


def test_hooks_env_modified():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs", "custom_dir": "theme_overrides"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "i18n": {
                "languages": [
                    {"locale": "en", "name": "english", "default": True},
                    {"locale": "fr", "name": "français"},
                ],
            },
        },
        hooks=["hooks_jinja_on_env.py"],
        site_dir="/tmp/xoxo/",
    )
    build(mkdocs_config)

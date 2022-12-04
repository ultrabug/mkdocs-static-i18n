from mkdocs.commands.build import build
from mkdocs.config.base import load_config


def test_hooks_working():
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
            },
        },
        hooks=["hooks.py"],
    )
    build(mkdocs_config)

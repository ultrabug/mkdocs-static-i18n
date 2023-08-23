from pathlib import Path

from mkdocs.commands.build import build
from mkdocs.config.base import load_config


def test_rtd_fontfiles():
    config_base_rtd = load_config(
        "tests/mkdocs.yml",
        theme={"name": "readthedocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
    )

    config_plugin_rtd = load_config(
        "tests/mkdocs.yml",
        theme={"name": "readthedocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
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

    base_site_dir = config_base_rtd["site_dir"]
    i18n_site_dir = config_plugin_rtd["site_dir"]

    build(config_base_rtd)
    build(config_plugin_rtd)

    base_font_files = [
        str(p).replace(base_site_dir, "") for p in Path(base_site_dir, "fonts").glob("**/*")
    ]
    i18n_font_files = [
        str(p).replace(i18n_site_dir, "") for p in Path(i18n_site_dir, "fonts").glob("**/*")
    ]
    assert sorted(base_font_files) == sorted(i18n_font_files)

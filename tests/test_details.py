import re
import logging
from pathlib import Path

from mkdocs.commands.build import build
from mkdocs.config.base import load_config

def test_plugin_no_use_directory_urls_default_language_only():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "material"},
        docs_dir="details/",
        plugins={
            "i18n": {
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {
                        "locale": "fr",
                        "name": "français",
                        "build": True,
                        "admonition_translations": {
                            "tip": "Conseil",
                            "warning": "Avertissement",
                        }
                    },
                ],
            },
        },
        markdown_extensions=["admonition", "pymdownx.details"],
    )

    build(mkdocs_config)

    site_dir = mkdocs_config["site_dir"]

    with open(site_dir+'/index.html') as f:
        admonition_titles = re.findall(r"<summary>([^<]*)", f.read())
        assert(admonition_titles == ['Tip', 'Tip', 'Tip', 'Tip', 'Warning', 'Heey'])

    with open(site_dir+'/fr/index.html') as f:
        admonition_titles = re.findall(r"<summary>([^<]*)", f.read())
        assert(admonition_titles == ['Conseil', 'Conseil', 'Conseil', 'Conseil', 'Avertissement', 'Heey'])

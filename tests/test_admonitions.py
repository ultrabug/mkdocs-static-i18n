import re
import logging
from pathlib import Path

from mkdocs.commands.build import build
from mkdocs.config.base import load_config

ADMONITIONS_CONFIG_WARNING = "mkdocs_static_i18n: admonition_translations used, but admonitions won't be rendered properly without 'admonition' in mkdocs.yml's markdown_extensions."

class LogHandlerList(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def handle(self, record):
        rv = self.filter(record)
        if rv:
            # Use levelno for keys so they can be sorted later
            self.messages.append(record.getMessage())
        return rv

def test_invalid_config():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "material"},
        docs_dir="admonitions/",
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
    )
    
    warning_list = LogHandlerList()
    warning_list.setLevel(logging.WARNING)
    logging.getLogger('mkdocs').addHandler(warning_list)

    build(mkdocs_config)
    
    assert(ADMONITIONS_CONFIG_WARNING in warning_list.messages)
    

def test_plugin_no_use_directory_urls_default_language_only():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "material"},
        docs_dir="admonitions/",
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
        markdown_extensions=["admonition"],
    )

    warning_list = LogHandlerList()
    warning_list.setLevel(logging.WARNING)
    logging.getLogger('mkdocs').addHandler(warning_list)

    build(mkdocs_config)
    
    # assert(all(item == ADMONITIONS_CONFIG_WARNING) for item in warning_list.messages)
    assert(ADMONITIONS_CONFIG_WARNING not in warning_list.messages)
    
    site_dir = mkdocs_config["site_dir"]

    with open(site_dir+'/index.html') as f:
        admonition_titles = re.findall(r"<p class=[\"']admonition-title[\"']>([^<]*)", f.read())
        assert(admonition_titles == ['Tip', 'Tip', 'Warning', 'Heey'])

    with open(site_dir+'/fr/index.html') as f:
        admonition_titles = re.findall(r"<p class=[\"']admonition-title[\"']>([^<]*)", f.read())
        assert(admonition_titles == ['Conseil', 'Conseil', 'Avertissement', 'Heey'])

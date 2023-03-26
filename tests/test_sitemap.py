from pathlib import Path

import base
from bs4 import BeautifulSoup
from mkdocs.commands.build import build


def test_generic_both_alternates_enabled():
    """Expected 2 alternate entries, en for / and fr for /fr"""
    raw_config = base.create_config()

    _check_sitemap(raw_config=raw_config, num_of_alternates=2, num_of_links=3)


def test_generic_both_alternates_disabled():
    """Expected none alternate entries"""
    raw_config = base.create_config(
        plugin_options={
            "languages": {
                "en": {
                    "build": False,
                },
                "fr": {
                    "build": False,
                },
            },
        },
    )

    _check_sitemap(raw_config=raw_config, num_of_alternates=0, num_of_links=3)


def test_disabled_alternate_which_matches_default():
    """Expected 2 alternate entries, en for / and fr for /fr"""
    raw_config = base.create_config(
        plugin_options={
            "languages": {
                "en": {
                    "build": False,
                },
            },
        },
    )

    _check_sitemap(raw_config=raw_config, num_of_alternates=2, num_of_links=3)


def test_disabled_alternate_other_than_the_matching_default():
    """Expected none alternate entries"""
    raw_config = base.create_config(
        plugin_options={
            "languages": {
                "fr": {
                    "build": False,
                },
            },
        },
    )

    _check_sitemap(raw_config=raw_config, num_of_alternates=0, num_of_links=3)


def _check_sitemap(
    *, raw_config, num_of_alternates, num_of_links, hreflang_validators=None
):
    """The function builds the docs and checks the sitemap.
    All arguments refer to the sitemap not the config.
    """

    num_of_urls = max(num_of_alternates, 1) * num_of_links

    if hreflang_validators is None:
        hreflang_validators = {
            "en": lambda href: "/en/" not in href,
            "fr": lambda href: "/fr/" in href,
        }

    for _, mkdocs_config in base.load_configs(raw_config):
        build(mkdocs_config)
        soup = BeautifulSoup(
            (Path(mkdocs_config.site_dir) / "sitemap.xml").read_bytes(), "xml"
        )
        urls = soup.find_all("url")
        assert len(urls) == num_of_urls
        for url in urls:
            alternates = url.find_all("xhtml:link")
            assert len(alternates) == num_of_alternates
            for alternate in alternates:
                assert hreflang_validators[alternate["hreflang"]](alternate["href"])

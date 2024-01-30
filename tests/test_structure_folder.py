from pathlib import Path

import pytest
from mkdocs.commands.build import build
from mkdocs.config.base import load_config

USE_DIRECTORY_URLS = [
    Path("404.html"),
    Path("assets/image_non_localized.png"),
    Path("en/english_default/index.html"),
    Path("en/image.fake"),
    Path("en/image.png"),
    Path("en/index.html"),
    Path("en/topic1/named_file/index.html"),
    Path("en/topic2/1.1.filename.html"),
    Path("en/topic2/index.html"),
    Path("en/topic2/release_notes_17.1/index.html"),
    Path("en/topic2/release_notes_17.2/index.html"),
    Path("fr/french_only/index.html"),
    Path("fr/image.fake"),
    Path("fr/image.png"),
    Path("fr/index.html"),
    Path("fr/topic1/named_file/index.html"),
    Path("fr/topic2/1.1.filename.html"),
    Path("fr/topic2/index.html"),
]
NO_USE_DIRECTORY_URLS = [
    Path("404.html"),
    Path("assets/image_non_localized.png"),
    Path("en/english_default/index.html"),
    Path("en/image.fake"),
    Path("en/image.png"),
    Path("en/index.html"),
    Path("en/topic1/named_file.html"),
    Path("en/topic2/1.1.filename.html"),
    Path("en/topic2/index.html"),
    Path("en/topic2/release_notes_17.1.html"),
    Path("en/topic2/release_notes_17.2.html"),
    Path("fr/french_only/index.html"),
    Path("fr/image.fake"),
    Path("fr/image.png"),
    Path("fr/index.html"),
    Path("fr/topic1/named_file.html"),
    Path("fr/topic2/1.1.filename.html"),
    Path("fr/topic2/index.html"),
]


def test_build_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_folder_structure_two_languages/",
    )
    # Only strict=False run, because the files contain links,
    # which result in warning without the plugin.
    build(mkdocs_config)
    site_dir = mkdocs_config["site_dir"]
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.*")])
    assert sorted(generate_site) == sorted(USE_DIRECTORY_URLS)


def test_build_no_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_folder_structure_two_languages/",
    )
    # Only strict=False run, because the files contain links,
    # which result in warning without the plugin.
    build(mkdocs_config)
    site_dir = mkdocs_config["site_dir"]
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.*")])
    assert sorted(generate_site) == sorted(NO_USE_DIRECTORY_URLS)


PLUGIN_USE_DIRECTORY_URLS = [
    Path("404.html"),
    Path("assets/image_non_localized.png"),
    Path("english_default/index.html"),
    Path("image.fake"),
    Path("image.png"),
    Path("index.html"),
    Path("topic1/named_file/index.html"),
    Path("topic2/1.1.filename.html"),
    Path("topic2/index.html"),
    Path("topic2/release_notes_17.1/index.html"),
    Path("topic2/release_notes_17.2/index.html"),
    Path("fr/english_default/index.html"),
    Path("fr/french_only/index.html"),
    Path("fr/image.fake"),
    Path("fr/image.png"),
    Path("fr/index.html"),
    Path("fr/topic1/named_file/index.html"),
    Path("fr/topic2/1.1.filename.html"),
    Path("fr/topic2/index.html"),
    Path("fr/topic2/release_notes_17.1/index.html"),
    Path("fr/topic2/release_notes_17.2/index.html"),
]
PLUGIN_NO_USE_DIRECTORY_URLS = [
    Path("404.html"),
    Path("assets/image_non_localized.png"),
    Path("english_default/index.html"),
    Path("image.fake"),
    Path("image.png"),
    Path("index.html"),
    Path("topic1/named_file.html"),
    Path("topic2/1.1.filename.html"),
    Path("topic2/index.html"),
    Path("topic2/release_notes_17.1.html"),
    Path("topic2/release_notes_17.2.html"),
    Path("fr/english_default/index.html"),
    Path("fr/french_only/index.html"),
    Path("fr/image.fake"),
    Path("fr/image.png"),
    Path("fr/index.html"),
    Path("fr/topic1/named_file.html"),
    Path("fr/topic2/1.1.filename.html"),
    Path("fr/topic2/index.html"),
    Path("fr/topic2/release_notes_17.1.html"),
    Path("fr/topic2/release_notes_17.2.html"),
]


def test_plugin_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_folder_structure_two_languages/",
        plugins={
            "search": {},
            "i18n": {
                "docs_structure": "folder",
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
        strict=True,
    )
    try:
        build(mkdocs_config)
    except Exception as err:
        pytest.fail(reason=err)
    site_dir = mkdocs_config["site_dir"]
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.*")])
    assert sorted(generate_site) == sorted(PLUGIN_USE_DIRECTORY_URLS)


def test_plugin_use_directory_urls_static_nav():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_folder_structure_two_languages/",
        plugins={
            "search": {},
            "i18n": {
                "docs_structure": "folder",
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
        nav=[
            "index.md",
            "english_default/index.md",
            "topic1/named_file.md",
            "topic2/README.md",
            "topic2/release_notes_17.1.md",
            "topic2/release_notes_17.2.md",
        ],
        strict=True,
    )
    try:
        build(mkdocs_config)
    except Exception as err:
        pytest.fail(reason=err)
    site_dir = mkdocs_config["site_dir"]
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.*")])
    assert sorted(generate_site) == sorted(PLUGIN_USE_DIRECTORY_URLS)


def test_plugin_no_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_folder_structure_two_languages/",
        plugins={
            "search": {},
            "i18n": {
                "docs_structure": "folder",
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
        strict=True,
    )
    try:
        build(mkdocs_config)
    except Exception as err:
        pytest.fail(reason=err)
    site_dir = mkdocs_config["site_dir"]
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.*")])
    assert sorted(generate_site) == sorted(PLUGIN_NO_USE_DIRECTORY_URLS)


PLUGIN_USE_DIRECTORY_URLS_DEFAULT_ONLY = [
    Path("404.html"),
    Path("assets/image_non_localized.png"),
    Path("english_default/index.html"),
    Path("image.fake"),
    Path("image.png"),
    Path("index.html"),
    Path("topic1/named_file/index.html"),
    Path("topic2/1.1.filename.html"),
    Path("topic2/index.html"),
    Path("topic2/release_notes_17.1/index.html"),
    Path("topic2/release_notes_17.2/index.html"),
]
PLUGIN_NO_USE_DIRECTORY_URLS_DEFAULT_ONLY = [
    Path("404.html"),
    Path("assets/image_non_localized.png"),
    Path("english_default/index.html"),
    Path("image.fake"),
    Path("image.png"),
    Path("index.html"),
    Path("topic1/named_file.html"),
    Path("topic2/1.1.filename.html"),
    Path("topic2/index.html"),
    Path("topic2/release_notes_17.1.html"),
    Path("topic2/release_notes_17.2.html"),
]


def test_plugin_use_directory_urls_default_language_only():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_folder_structure_two_languages/",
        plugins={
            "search": {},
            "i18n": {
                "docs_structure": "folder",
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français", "build": False},
                ],
            },
        },
        strict=True,
    )
    try:
        build(mkdocs_config)
    except Exception as err:
        pytest.fail(reason=err)
    site_dir = mkdocs_config["site_dir"]
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.*")])
    assert sorted(generate_site) == sorted(PLUGIN_USE_DIRECTORY_URLS_DEFAULT_ONLY)


def test_plugin_no_use_directory_urls_default_language_only():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_folder_structure_two_languages/",
        plugins={
            "search": {},
            "i18n": {
                "docs_structure": "folder",
                "languages": [
                    {
                        "locale": "en",
                        "name": "english",
                        "default": True,
                    },
                    {"locale": "fr", "name": "français", "build": False},
                ],
            },
        },
        strict=True,
    )
    try:
        build(mkdocs_config)
    except Exception as err:
        pytest.fail(reason=err)
    site_dir = mkdocs_config["site_dir"]
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.*")])
    assert sorted(generate_site) == sorted(PLUGIN_NO_USE_DIRECTORY_URLS_DEFAULT_ONLY)

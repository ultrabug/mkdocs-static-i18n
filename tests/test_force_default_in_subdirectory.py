from pathlib import Path

import pytest
from mkdocs.commands.build import build
from mkdocs.config.base import load_config

# Folder structure test cases
FOLDER_NO_USE_DIRECTORY_URLS = [
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

# Test cases for force_default_in_subdirectory=True
FOLDER_FORCE_DEFAULT_USE_DIRECTORY_URLS = [
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

# Suffix structure test cases
SUFFIX_NO_USE_DIRECTORY_URLS = [
    Path("english_default/index.html"),
    Path("404.html"),
    Path("image.png"),
    Path("image.fake"),
    Path("index.html"),
    Path("assets/image_non_localized.png"),
    Path("topic1/named_file.html"),
    Path("topic2/index.html"),
    Path("topic2/1.1.filename.html"),
    Path("topic2/release_notes_17.1.html"),
    Path("topic2/release_notes_17.2.html"),
    Path("fr/index.html"),
    Path("fr/image.png"),
    Path("fr/image.fake"),
    Path("fr/english_default/index.html"),
    Path("fr/topic1/named_file.html"),
    Path("fr/topic2/index.html"),
    Path("fr/topic2/1.1.filename.html"),
    Path("fr/french_only/index.html"),
    Path("fr/topic2/release_notes_17.1.html"),
    Path("fr/topic2/release_notes_17.2.html"),
]

SUFFIX_FORCE_DEFAULT_USE_DIRECTORY_URLS = [
    Path("404.html"),
    Path("en/assets/image_non_localized.png"),
    Path("en/english_default/index.html"),
    Path("en/image.fake"),
    Path("en/image.png"),
    Path("en/index.html"),
    Path("en/topic1/named_file/index.html"),
    Path("en/topic2/1.1.filename.html"),
    Path("en/topic2/index.html"),
    Path("en/topic2/release_notes_17.1/index.html"),
    Path("en/topic2/release_notes_17.2/index.html"),
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

# Folder structure tests
def test_folder_force_default_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_folder_structure_two_languages/",
        plugins={
            "search": {},
            "i18n": {
                "docs_structure": "folder",
                "force_default_in_subdirectory": True,
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
    assert sorted(generate_site) == sorted(FOLDER_FORCE_DEFAULT_USE_DIRECTORY_URLS)

def test_folder_force_default_no_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_folder_structure_two_languages/",
        plugins={
            "search": {},
            "i18n": {
                "docs_structure": "folder",
                "force_default_in_subdirectory": False,
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
    assert sorted(generate_site) == sorted(FOLDER_NO_USE_DIRECTORY_URLS)

# Suffix structure tests
def test_suffix_force_default_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure_two_languages/",
        plugins={
            "search": {},
            "i18n": {
                "docs_structure": "suffix",
                "force_default_in_subdirectory": True,
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
    assert sorted(generate_site) == sorted(SUFFIX_FORCE_DEFAULT_USE_DIRECTORY_URLS)

def test_suffix_force_default_no_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_suffix_structure_two_languages/",
        plugins={
            "search": {},
            "i18n": {
                "docs_structure": "suffix",
                "force_default_in_subdirectory": False,
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
    assert sorted(generate_site) == sorted(SUFFIX_NO_USE_DIRECTORY_URLS)
from pathlib import Path

from mkdocs.commands.build import build
from mkdocs.config.base import load_config

USE_DIRECTORY_URLS = [
    Path("english_default/index.en/index.html"),
    Path("404.html"),
    Path("assets/image_non_localized.png"),
    Path("french_only/index.fr/index.html"),
    Path("image.en.fake"),
    Path("image.en.png"),
    Path("image.fr.fake"),
    Path("image.fr.png"),
    Path("index.fr/index.html"),
    Path("index.html"),
    Path("topic1/named_file.en/index.html"),
    Path("topic1/named_file.fr/index.html"),
    Path("topic2/1.1.filename.fr.html"),
    Path("topic2/1.1.filename.html"),
    Path("topic2/index.html"),
    Path("topic2/README.fr/index.html"),
]
NO_USE_DIRECTORY_URLS = [
    Path("english_default/index.en.html"),
    Path("404.html"),
    Path("assets/image_non_localized.png"),
    Path("french_only/index.fr.html"),
    Path("image.en.fake"),
    Path("image.en.png"),
    Path("image.fr.fake"),
    Path("image.fr.png"),
    Path("index.fr.html"),
    Path("index.html"),
    Path("topic1/named_file.en.html"),
    Path("topic1/named_file.fr.html"),
    Path("topic2/1.1.filename.fr.html"),
    Path("topic2/1.1.filename.html"),
    Path("topic2/index.html"),
    Path("topic2/README.fr.html"),
]


def test_build_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
    )
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
        docs_dir="docs_suffix_structure/",
    )
    build(mkdocs_config)
    site_dir = mkdocs_config["site_dir"]
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.*")])
    assert sorted(generate_site) == sorted(NO_USE_DIRECTORY_URLS)


PLUGIN_USE_DIRECTORY_URLS = [
    Path("english_default/index.html"),
    Path("404.html"),
    Path("image.png"),
    Path("image.fake"),
    Path("index.html"),
    Path("assets/image_non_localized.png"),
    Path("topic1/named_file/index.html"),
    Path("topic2/index.html"),
    Path("topic2/1.1.filename.html"),
    Path("fr/index.html"),
    Path("fr/image.png"),
    Path("fr/image.fake"),
    Path("fr/english_default/index.html"),
    Path("fr/topic1/named_file/index.html"),
    Path("fr/topic2/index.html"),
    Path("fr/topic2/1.1.filename.html"),
    Path("fr/french_only/index.html"),
]
PLUGIN_NO_USE_DIRECTORY_URLS = [
    Path("english_default/index.html"),
    Path("404.html"),
    Path("image.png"),
    Path("image.fake"),
    Path("index.html"),
    Path("assets/image_non_localized.png"),
    Path("topic1/named_file.html"),
    Path("topic2/index.html"),
    Path("topic2/1.1.filename.html"),
    Path("fr/index.html"),
    Path("fr/image.png"),
    Path("fr/image.fake"),
    Path("fr/english_default/index.html"),
    Path("fr/topic1/named_file.html"),
    Path("fr/topic2/index.html"),
    Path("fr/topic2/1.1.filename.html"),
    Path("fr/french_only/index.html"),
]


def test_plugin_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "search": {},
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
    build(mkdocs_config)
    site_dir = mkdocs_config["site_dir"]
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.*")])
    assert sorted(generate_site) == sorted(PLUGIN_USE_DIRECTORY_URLS)


def test_plugin_use_directory_urls_static_nav():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "search": {},
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
        nav=[
            {
                "Home": "index.md",
            }
        ],
    )
    build(mkdocs_config)
    site_dir = mkdocs_config["site_dir"]
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.*")])
    assert sorted(generate_site) == sorted(PLUGIN_USE_DIRECTORY_URLS)


def test_plugin_no_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_suffix_structure/",
        plugins={
            "search": {},
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
    build(mkdocs_config)
    site_dir = mkdocs_config["site_dir"]
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.*")])
    assert sorted(generate_site) == sorted(PLUGIN_NO_USE_DIRECTORY_URLS)


PLUGIN_USE_DIRECTORY_URLS_DEFAULT_ONLY = [
    Path("404.html"),
    Path("image.png"),
    Path("image.fake"),
    Path("index.html"),
    Path("assets/image_non_localized.png"),
    Path("english_default/index.html"),
    Path("topic1/named_file/index.html"),
    Path("topic2/index.html"),
    Path("topic2/1.1.filename.html"),
]
PLUGIN_NO_USE_DIRECTORY_URLS_DEFAULT_ONLY = [
    Path("404.html"),
    Path("image.png"),
    Path("image.fake"),
    Path("index.html"),
    Path("assets/image_non_localized.png"),
    Path("english_default/index.html"),
    Path("topic1/named_file.html"),
    Path("topic2/index.html"),
    Path("topic2/1.1.filename.html"),
]


def test_plugin_use_directory_urls_default_language_only():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "search": {},
            "i18n": {
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
    )
    build(mkdocs_config)
    site_dir = mkdocs_config["site_dir"]
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.*")])
    assert sorted(generate_site) == sorted(PLUGIN_USE_DIRECTORY_URLS_DEFAULT_ONLY)


def test_plugin_no_use_directory_urls_default_language_only():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_suffix_structure/",
        plugins={
            "search": {},
            "i18n": {
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
    )
    build(mkdocs_config)
    site_dir = mkdocs_config["site_dir"]
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.*")])
    assert sorted(generate_site) == sorted(PLUGIN_NO_USE_DIRECTORY_URLS_DEFAULT_ONLY)

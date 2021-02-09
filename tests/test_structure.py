from pathlib import Path

from mkdocs.commands.build import build

USE_DIRECTORY_URLS = [
    "404.html",
    "test.en/index.html",
    "test.fr/index.html",
    "folder/tata/index.html",
    "folder/toto/index.html",
]
NO_USE_DIRECTORY_URLS = [
    "404.html",
    "test.en.html",
    "test.fr.html",
    "folder/tata.html",
    "folder/toto.html",
]

PLUGIN_USE_DIRECTORY_URLS = [
    "404.html",
    "index.html",
    "folder/tata/index.html",
    "folder/toto/index.html",
    "en/index.html",
    "en/folder/tata/index.html",
    "en/folder/toto/index.html",
    "fr/index.html",
    "fr/folder/tata/index.html",
    "fr/folder/toto/index.html",
]
PLUGIN_NO_USE_DIRECTORY_URLS = [
    "404.html",
    "test.html",
    "folder/tata.html",
    "folder/toto.html",
    "en/test.html",
    "en/folder/tata.html",
    "en/folder/toto.html",
    "fr/test.html",
    "fr/folder/tata.html",
    "fr/folder/toto.html",
]


def test_build_use_directory_urls(config_base):
    config_base["use_directory_urls"] = True
    site_dir = config_base["site_dir"]
    build(config_base)
    generated_html = [
        f.relative_to(site_dir).as_posix() for f in Path(site_dir).glob("**/*.html")
    ]
    assert sorted(generated_html) == sorted(USE_DIRECTORY_URLS)


def test_build_no_use_directory_urls(config_base):
    config_base["use_directory_urls"] = False
    site_dir = config_base["site_dir"]
    build(config_base)
    generated_html = [
        f.relative_to(site_dir).as_posix() for f in Path(site_dir).glob("**/*.html")
    ]
    assert sorted(generated_html) == sorted(NO_USE_DIRECTORY_URLS)


def test_plugin_use_directory_urls(config_plugin):
    config_plugin["use_directory_urls"] = True
    site_dir = config_plugin["site_dir"]
    build(config_plugin)
    generated_html = [
        f.relative_to(site_dir).as_posix() for f in Path(site_dir).glob("**/*.html")
    ]
    assert sorted(generated_html) == sorted(PLUGIN_USE_DIRECTORY_URLS)


def test_plugin_no_use_directory_urls(config_plugin):
    config_plugin["use_directory_urls"] = False
    site_dir = config_plugin["site_dir"]
    build(config_plugin)
    generated_html = [
        f.relative_to(site_dir).as_posix() for f in Path(site_dir).glob("**/*.html")
    ]
    assert sorted(generated_html) == sorted(PLUGIN_NO_USE_DIRECTORY_URLS)

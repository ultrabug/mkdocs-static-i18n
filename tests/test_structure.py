from pathlib import Path

from mkdocs.commands.build import build

USE_DIRECTORY_URLS = [
    "404.html",
    "test.en/index.html",
    "test.fr/index.html",
    "folder_01/tata/index.html",
    "folder_01/toto/index.html",
    "folder_02/tete.en/index.html",
    "folder_02/tete.fr/index.html",
]
NO_USE_DIRECTORY_URLS = [
    "404.html",
    "test.en.html",
    "test.fr.html",
    "folder_01/tata.html",
    "folder_01/toto.html",
    "folder_02/tete.en.html",
    "folder_02/tete.fr.html",
]

PLUGIN_USE_DIRECTORY_URLS = [
    "404.html",
    "index.html",
    "folder_01/tata/index.html",
    "folder_01/toto/index.html",
    "folder_02/index.html",
    "en/index.html",
    "en/folder_01/tata/index.html",
    "en/folder_01/toto/index.html",
    "en/folder_02/index.html",
    "fr/index.html",
    "fr/folder_01/tata/index.html",
    "fr/folder_01/toto/index.html",
    "fr/folder_02/index.html",
]
PLUGIN_NO_USE_DIRECTORY_URLS = [
    "404.html",
    "test.html",
    "folder_01/tata.html",
    "folder_01/toto.html",
    "folder_02/tete.html",
    "en/test.html",
    "en/folder_01/tata.html",
    "en/folder_01/toto.html",
    "en/folder_02/tete.html",
    "fr/test.html",
    "fr/folder_01/tata.html",
    "fr/folder_01/toto.html",
    "fr/folder_02/tete.html",
]

PLUGIN_USE_DIRECTORY_URLS_NO_DEFAULT = [
    "404.html",
    "index.html",
    "folder_01/tata/index.html",
    "folder_01/toto/index.html",
    "folder_02/index.html",
    "fr/index.html",
    "fr/folder_01/tata/index.html",
    "fr/folder_01/toto/index.html",
    "fr/folder_02/index.html",
]
PLUGIN_NO_USE_DIRECTORY_URLS_NO_DEFAULT = [
    "404.html",
    "test.html",
    "folder_01/tata.html",
    "folder_01/toto.html",
    "folder_02/tete.html",
    "fr/test.html",
    "fr/folder_01/tata.html",
    "fr/folder_01/toto.html",
    "fr/folder_02/tete.html",
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


def test_plugin_use_directory_urls_no_default_language(
    config_plugin_no_default_language,
):
    config_plugin_no_default_language["use_directory_urls"] = True
    site_dir = config_plugin_no_default_language["site_dir"]
    build(config_plugin_no_default_language)
    generated_html = [
        f.relative_to(site_dir).as_posix() for f in Path(site_dir).glob("**/*.html")
    ]
    assert sorted(generated_html) == sorted(PLUGIN_USE_DIRECTORY_URLS_NO_DEFAULT)


def test_plugin_no_use_directory_urls_no_default_language(
    config_plugin_no_default_language,
):
    config_plugin_no_default_language["use_directory_urls"] = False
    site_dir = config_plugin_no_default_language["site_dir"]
    build(config_plugin_no_default_language)
    generated_html = [
        f.relative_to(site_dir).as_posix() for f in Path(site_dir).glob("**/*.html")
    ]
    assert sorted(generated_html) == sorted(PLUGIN_NO_USE_DIRECTORY_URLS_NO_DEFAULT)

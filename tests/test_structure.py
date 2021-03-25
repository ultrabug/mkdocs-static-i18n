from pathlib import Path

from mkdocs.commands.build import build

USE_DIRECTORY_URLS = [
    Path("404.html"),
    Path("test.en/index.html"),
    Path("test.fr/index.html"),
    Path("folder/tata/index.html"),
    Path("folder/toto/index.html"),
]
NO_USE_DIRECTORY_URLS = [
    Path("404.html"),
    Path("test.en.html"),
    Path("test.fr.html"),
    Path("folder/tata.html"),
    Path("folder/toto.html"),
]

PLUGIN_USE_DIRECTORY_URLS = [
    Path("404.html"),
    Path("index.html"),
    Path("folder/tata/index.html"),
    Path("folder/toto/index.html"),
    Path("en/index.html"),
    Path("en/folder/tata/index.html"),
    Path("en/folder/toto/index.html"),
    Path("fr/index.html"),
    Path("fr/folder/tata/index.html"),
    Path("fr/folder/toto/index.html"),
]
PLUGIN_NO_USE_DIRECTORY_URLS = [
    Path("404.html"),
    Path("test.html"),
    Path("folder/tata.html"),
    Path("folder/toto.html"),
    Path("en/test.html"),
    Path("en/folder/tata.html"),
    Path("en/folder/toto.html"),
    Path("fr/test.html"),
    Path("fr/folder/tata.html"),
    Path("fr/folder/toto.html"),
]

PLUGIN_USE_DIRECTORY_URLS_NO_DEFAULT = [
    Path("404.html"),
    Path("index.html"),
    Path("folder/tata/index.html"),
    Path("folder/toto/index.html"),
    Path("fr/index.html"),
    Path("fr/folder/tata/index.html"),
    Path("fr/folder/toto/index.html"),
]
PLUGIN_NO_USE_DIRECTORY_URLS_NO_DEFAULT = [
    Path("404.html"),
    Path("test.html"),
    Path("folder/tata.html"),
    Path("folder/toto.html"),
    Path("fr/test.html"),
    Path("fr/folder/tata.html"),
    Path("fr/folder/toto.html"),
]


def test_build_use_directory_urls(config_base):
    config_base["use_directory_urls"] = True
    site_dir = config_base["site_dir"]
    build(config_base)
    generated_html = [
        f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")
    ]
    print(list(Path(site_dir).glob("**/*.html")))
    assert sorted(generated_html) == sorted(USE_DIRECTORY_URLS)


def test_build_no_use_directory_urls(config_base):
    config_base["use_directory_urls"] = False
    site_dir = config_base["site_dir"]
    build(config_base)
    generated_html = [
        f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")
    ]
    print(list(Path(site_dir).glob("**/*.html")))
    assert sorted(generated_html) == sorted(NO_USE_DIRECTORY_URLS)


def test_plugin_use_directory_urls(config_plugin):
    config_plugin["use_directory_urls"] = True
    site_dir = config_plugin["site_dir"]
    build(config_plugin)
    generated_html = [
        f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")
    ]
    print(list(Path(site_dir).glob("**/*.html")))
    assert sorted(generated_html) == sorted(PLUGIN_USE_DIRECTORY_URLS)


def test_plugin_no_use_directory_urls(config_plugin):
    config_plugin["use_directory_urls"] = False
    site_dir = config_plugin["site_dir"]
    build(config_plugin)
    generated_html = [
        f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")
    ]
    print(list(Path(site_dir).glob("**/*.html")))
    assert sorted(generated_html) == sorted(PLUGIN_NO_USE_DIRECTORY_URLS)


def test_plugin_use_directory_urls_no_default_language(
    config_plugin_no_default_language,
):
    config_plugin_no_default_language["use_directory_urls"] = True
    site_dir = config_plugin_no_default_language["site_dir"]
    build(config_plugin_no_default_language)
    generated_html = [
        f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")
    ]
    print(list(Path(site_dir).glob("**/*.html")))
    assert sorted(generated_html) == sorted(PLUGIN_USE_DIRECTORY_URLS_NO_DEFAULT)


def test_plugin_no_use_directory_urls_no_default_language(
    config_plugin_no_default_language,
):
    config_plugin_no_default_language["use_directory_urls"] = False
    site_dir = config_plugin_no_default_language["site_dir"]
    build(config_plugin_no_default_language)
    generated_html = [
        f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")
    ]
    print(list(Path(site_dir).glob("**/*.html")))
    assert sorted(generated_html) == sorted(PLUGIN_NO_USE_DIRECTORY_URLS_NO_DEFAULT)

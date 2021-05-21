from pathlib import Path

from mkdocs.commands.build import build

USE_DIRECTORY_URLS = [
    Path("404.html"),
    Path("image.en.png"),
    Path("image.fr.png"),
    Path("index.fr/index.html"),
    Path("index.html"),
    Path("topic1/named_file.en/index.html"),
    Path("topic1/named_file.fr/index.html"),
    Path("topic2/index.en/index.html"),
    Path("topic2/index.html"),
]
NO_USE_DIRECTORY_URLS = [
    Path("404.html"),
    Path("image.en.png"),
    Path("image.fr.png"),
    Path("index.fr.html"),
    Path("index.html"),
    Path("topic1/named_file.en.html"),
    Path("topic1/named_file.fr.html"),
    Path("topic2/index.en.html"),
    Path("topic2/index.html"),
]


def test_build_use_directory_urls(config_base):
    config_base["use_directory_urls"] = True
    site_dir = config_base["site_dir"]
    build(config_base)
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.png")])
    print(list(Path(site_dir).glob("**/*.html")))
    assert sorted(generate_site) == sorted(USE_DIRECTORY_URLS)


def test_build_no_use_directory_urls(config_base):
    config_base["use_directory_urls"] = False
    site_dir = config_base["site_dir"]
    build(config_base)
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.png")])
    print(list(Path(site_dir).glob("**/*.html")))
    assert sorted(generate_site) == sorted(NO_USE_DIRECTORY_URLS)


PLUGIN_USE_DIRECTORY_URLS = [
    Path("404.html"),
    Path("image.png"),
    Path("index.html"),
    Path("topic1/named_file/index.html"),
    Path("topic2/index.html"),
    Path("en/index.html"),
    Path("en/image.png"),
    Path("en/topic1/named_file/index.html"),
    Path("en/topic2/index.html"),
    Path("fr/index.html"),
    Path("fr/image.png"),
    Path("fr/topic1/named_file/index.html"),
    Path("fr/topic2/index.html"),
]
PLUGIN_NO_USE_DIRECTORY_URLS = [
    Path("404.html"),
    Path("image.png"),
    Path("index.html"),
    Path("topic1/named_file.html"),
    Path("topic2/index.html"),
    Path("en/index.html"),
    Path("en/image.png"),
    Path("en/topic1/named_file.html"),
    Path("en/topic2/index.html"),
    Path("fr/index.html"),
    Path("fr/image.png"),
    Path("fr/topic1/named_file.html"),
    Path("fr/topic2/index.html"),
]


def test_plugin_use_directory_urls(config_plugin):
    config_plugin["use_directory_urls"] = True
    site_dir = config_plugin["site_dir"]
    build(config_plugin)
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.png")])
    print(list(Path(site_dir).glob("**/*.html")))
    assert sorted(generate_site) == sorted(PLUGIN_USE_DIRECTORY_URLS)


def test_plugin_no_use_directory_urls(config_plugin):
    config_plugin["use_directory_urls"] = False
    site_dir = config_plugin["site_dir"]
    build(config_plugin)
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.png")])
    print(list(Path(site_dir).glob("**/*.html")))
    assert sorted(generate_site) == sorted(PLUGIN_NO_USE_DIRECTORY_URLS)


PLUGIN_USE_DIRECTORY_URLS_NO_DEFAULT = [
    Path("404.html"),
    Path("image.png"),
    Path("index.html"),
    Path("topic1/named_file/index.html"),
    Path("topic2/index.html"),
    Path("fr/index.html"),
    Path("fr/image.png"),
    Path("fr/topic1/named_file/index.html"),
    Path("fr/topic2/index.html"),
]
PLUGIN_NO_USE_DIRECTORY_URLS_NO_DEFAULT = [
    Path("404.html"),
    Path("image.png"),
    Path("index.html"),
    Path("topic1/named_file.html"),
    Path("topic2/index.html"),
    Path("fr/index.html"),
    Path("fr/image.png"),
    Path("fr/topic1/named_file.html"),
    Path("fr/topic2/index.html"),
]


def test_plugin_use_directory_urls_no_default_language(
    config_plugin_no_default_language,
):
    config_plugin_no_default_language["use_directory_urls"] = True
    site_dir = config_plugin_no_default_language["site_dir"]
    build(config_plugin_no_default_language)
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.png")])
    print(list(Path(site_dir).glob("**/*.html")))
    assert sorted(generate_site) == sorted(PLUGIN_USE_DIRECTORY_URLS_NO_DEFAULT)


def test_plugin_no_use_directory_urls_no_default_language(
    config_plugin_no_default_language,
):
    config_plugin_no_default_language["use_directory_urls"] = False
    site_dir = config_plugin_no_default_language["site_dir"]
    build(config_plugin_no_default_language)
    generate_site = [f.relative_to(site_dir) for f in Path(site_dir).glob("**/*.html")]
    generate_site.extend([f.relative_to(site_dir) for f in Path(site_dir).glob("**/image*.png")])
    print(list(Path(site_dir).glob("**/*.html")))
    assert sorted(generate_site) == sorted(PLUGIN_NO_USE_DIRECTORY_URLS_NO_DEFAULT)

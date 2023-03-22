from mkdocs.config.base import load_config
from mkdocs.structure.files import get_files


def test_urls_no_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_suffix_structure/",
    )
    files = get_files(mkdocs_config)
    #
    mkdocs_i18n_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=False,
        docs_dir="docs_suffix_structure/",
        plugins={
            "i18n": {
                "default_language": "en",
                "languages": {"fr": "français", "en": "english"},
            },
        },
    )
    i18n_plugin = mkdocs_i18n_config["plugins"]["i18n"]
    #
    i18n_plugin.on_config(mkdocs_i18n_config)
    i18n_files = i18n_plugin.on_files(get_files(mkdocs_i18n_config), mkdocs_i18n_config)
    #
    mkdocs_urls = set()
    for page in files.documentation_pages():
        for lang in i18n_plugin.config["languages"]:
            page.url = page.url.replace(f".{lang}", "").replace("README", "index")
        mkdocs_urls.add(page.url)
    plugin_urls = {p.url for p in i18n_files.documentation_pages()}
    assert mkdocs_urls == plugin_urls


def test_urls_use_directory_urls():
    mkdocs_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
    )
    files = get_files(mkdocs_config)
    #
    mkdocs_i18n_config = load_config(
        "tests/mkdocs.yml",
        theme={"name": "mkdocs"},
        use_directory_urls=True,
        docs_dir="docs_suffix_structure/",
        plugins={
            "i18n": {
                "default_language": "en",
                "languages": {"fr": "français", "en": "english"},
            },
        },
    )
    i18n_plugin = mkdocs_i18n_config["plugins"]["i18n"]
    #
    i18n_plugin.on_config(mkdocs_i18n_config)
    i18n_files = i18n_plugin.on_files(get_files(mkdocs_i18n_config), mkdocs_i18n_config)
    #
    mkdocs_urls = set()
    for page in files.documentation_pages():
        if "index" in page.url:
            continue
        for lang in i18n_plugin.config["languages"]:
            page.url = page.url.replace(f".{lang}", "").replace("README/", "")
        mkdocs_urls.add(page.url)
    plugin_urls = {p.url for p in i18n_files.documentation_pages()}
    assert mkdocs_urls == plugin_urls

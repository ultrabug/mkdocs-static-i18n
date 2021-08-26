from mkdocs.structure.files import get_files


def test_urls_no_use_directory_urls(config_base, config_plugin):
    config_base["use_directory_urls"] = False
    files = get_files(config_base)
    #
    config_plugin["use_directory_urls"] = False
    i18n_plugin = config_plugin["plugins"]["i18n"]
    #
    i18n_plugin.on_config(config_plugin)
    i18n_files = i18n_plugin.on_files(get_files(config_plugin), config_plugin)
    #
    mkdocs_urls = set()
    for page in files.documentation_pages():
        for lang in i18n_plugin.config["languages"]:
            page.url = page.url.replace(f".{lang}", "")
        mkdocs_urls.add(page.url)
    plugin_urls = {p.url for p in i18n_files.documentation_pages()}
    assert mkdocs_urls == plugin_urls


def test_urls_use_directory_urls(config_base, config_plugin):
    config_base["use_directory_urls"] = True
    files = get_files(config_base)
    #
    config_plugin["use_directory_urls"] = True
    i18n_plugin = config_plugin["plugins"]["i18n"]
    #
    i18n_plugin.on_config(config_plugin)
    i18n_files = i18n_plugin.on_files(get_files(config_plugin), config_plugin)
    #
    mkdocs_urls = set()
    for page in files.documentation_pages():
        if "index" in page.url:
            continue
        for lang in i18n_plugin.config["languages"]:
            page.url = page.url.replace(f".{lang}", "")
        mkdocs_urls.add(page.url)
    plugin_urls = {p.url for p in i18n_files.documentation_pages()}
    assert mkdocs_urls == plugin_urls

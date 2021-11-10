from mkdocs.commands.build import build


def test_search_add_lang(config_plugin_search):
    config = config_plugin_search
    build(config)
    search_plugin = config["plugins"]["search"]
    assert search_plugin.config["lang"] == ["en", "fr"]


def test_search_entries(config_plugin_search):
    config = config_plugin_search
    config["plugins"]["i18n"].config["languages"] = {"fr": "français"}
    build(config)
    search_plugin = config["plugins"]["search"]
    assert len(search_plugin.search_index._entries) == 30


def test_search_entries_no_directory_urls(config_plugin_search):
    config = config_plugin_search
    config["use_directory_urls"] = False
    config["plugins"]["i18n"].config["languages"] = {"fr": "français"}
    build(config)
    search_plugin = config["plugins"]["search"]
    assert len(search_plugin.search_index._entries) == 30


def test_search_deduplicate_entries(config_plugin_search):
    config = config_plugin_search
    build(config)
    search_plugin = config["plugins"]["search"]
    assert len(search_plugin.search_index._entries) == 33


def test_search_deduplicate_entries_no_directory_urls(config_plugin_search):
    config = config_plugin_search
    config["use_directory_urls"] = False
    build(config)
    search_plugin = config["plugins"]["search"]
    assert len(search_plugin.search_index._entries) == 35

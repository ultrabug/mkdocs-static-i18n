from mkdocs.commands.build import build


def test_sitemap(config_plugin):
    build(config_plugin)
    i18n_plugin = config_plugin["plugins"]["i18n"]
    #
    expected_urls = [
        f"{config_plugin['site_url']}{p.url}"
        for p in i18n_plugin.sitemap_pages
        if p.url != "."
    ]
    sitemap = open(f"{config_plugin['site_dir']}/sitemap.xml").read()
    for url in expected_urls:
        assert url in sitemap

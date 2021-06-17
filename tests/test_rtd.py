from pathlib import Path

from mkdocs.commands.build import build


def test_rtd_fontfiles(config_base_rtd, config_plugin_rtd):
    base_site_dir = config_base_rtd["site_dir"]
    i18n_site_dir = config_plugin_rtd["site_dir"]

    build(config_base_rtd)
    build(config_plugin_rtd)

    base_font_files = [
        str(p).replace(base_site_dir, "")
        for p in Path(base_site_dir, "fonts").glob("**/*")
    ]
    i18n_font_files = [
        str(p).replace(i18n_site_dir, "")
        for p in Path(i18n_site_dir, "fonts").glob("**/*")
    ]
    assert sorted(base_font_files) == sorted(i18n_font_files)

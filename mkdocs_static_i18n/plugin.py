import logging
from pathlib import PurePath
from typing import Optional

from jinja2.ext import loopcontrols
from mkdocs import plugins
from mkdocs.commands.build import build
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from mkdocs_static_i18n import suffix
from mkdocs_static_i18n.reconfigure import ExtendedPlugin

try:
    from importlib.metadata import files as package_files
    from importlib.metadata import version

    material_version = version("mkdocs-material")
    material_languages = [
        lang.stem
        for lang in package_files("mkdocs-material")
        if "material/partials/languages" in lang.as_posix()
    ]
except Exception:
    try:
        # python 3.7 compatibility, drop on 3.7 EOL
        import pkg_resources

        material_dist = pkg_resources.get_distribution("mkdocs-material")
        material_version = material_dist.version
        material_languages = [
            lang.split(".html")[0]
            for lang in material_dist.resource_listdir("material/partials/languages")
        ]
    except Exception:
        material_languages = []
        material_version = None

log = logging.getLogger("mkdocs.plugins." + __name__)


class I18n(ExtendedPlugin):
    """
    We use 'event_priority' to make sure that we are last plugin to be executed
    because we need to make sure that we react to other plugins' behavior
    properly.

    Current plugins we heard of and require that we control their order:
        - awesome-pages: this plugin should run before us
        - with-pdf: this plugin is triggerd by us on the appropriate on_* events
    """

    @plugins.event_priority(-100)
    def on_config(self, config: MkDocsConfig):
        """
        Enrich configuration with language specific knowledge.
        """
        # first execution, setup defaults
        if self.current_language is None:
            self.current_language = self.default_language
        # reconfigure the mkdocs config
        return self.reconfigure_mkdocs_config(config)

    @plugins.event_priority(-100)
    def on_files(self, files: Files, config: MkDocsConfig):
        """
        Construct the lang specific file tree which will be used to
        generate the navigation for the default site and per language.
        """
        if self.config["docs_structure"] == "suffix":
            i18n_files = suffix.on_files(self, files, config)
        else:
            raise Exception("unimplemented")
        # reconfigure the alternates map by build language
        self.i18n_alternates = self.reconfigure_alternates(i18n_files)
        return i18n_files

    @plugins.event_priority(-100)
    def on_nav(self, nav, config, files):
        """
        Translate i18n aware navigation to honor the 'nav_translations' option.
        """

        homepage_suffix: str = "" if config.use_directory_urls else "index.html"

        # maybe move to another file and don't pass it as parameter?
        class NavHelper:
            translated_items: int = 0
            homepage: Optional[Page] = nav.homepage
            expected_homepage_urls = [
                f"{self.current_language}/{homepage_suffix}",
                f"/{self.current_language}/{homepage_suffix}",
            ]

        i18n_nav = self.reconfigure_navigation(nav, config, files, NavHelper)
        i18n_nav.homepage = NavHelper.homepage

        # report translated entries
        if NavHelper.translated_items:
            log.info(
                f"Translated {NavHelper.translated_items} navigation element"
                f"{'s' if NavHelper.translated_items > 1 else ''} to '{self.current_language}'"
            )

        # report missing homepage
        if i18n_nav.homepage is None:
            log.warning(f"Could not find a homepage for locale '{self.current_language}'")

        # manually trigger with-pdf, see #110
        with_pdf_plugin = config["plugins"].get("with-pdf")
        if with_pdf_plugin:
            with_pdf_plugin.on_nav(i18n_nav, config, files)

        return i18n_nav

    def on_env(self, env, config, files):
        # Add extension to allow the "continue" clause in the sitemap template loops.
        env.add_extension(loopcontrols)

    @plugins.event_priority(-100)
    def on_template_context(self, context, template_name, config):
        """
        Template context only applies to Template() objects.
        We add some metadata for users and our sitemap.xml generation.
        """
        # convenience for users in case they need it (we don't)
        context["i18n_build_languages"] = self.build_languages
        context["i18n_current_language_config"] = self.current_language_config
        context["i18n_current_language"] = self.current_language
        # used by sitemap.xml template
        context["i18n_alternates"] = self.i18n_alternates
        return context

    @plugins.event_priority(-100)
    def on_page_context(self, context, page, config, nav):
        """
        Page context only applies to Page() objects.
        We add some metadata for users as well as some neat reconfiguration features.

        Overriden templates such as the sitemap.xml are not impacted by this method!
        """
        # export some useful i18n related variables on page context, see #75
        context["i18n_config"] = self.config
        context["i18n_page_locale"] = page.file.locale
        if self.config["reconfigure_material"] is True:
            context = self.reconfigure_page_context(context, page, config, nav)
        return context

    @plugins.event_priority(-100)
    def on_post_page(self, output, page, config):
        """
        Some plugins we control ourselves need this event.
        """
        # manually trigger with-pdf, see #110
        with_pdf_plugin = config["plugins"].get("with-pdf")
        if with_pdf_plugin:
            with_pdf_plugin.on_post_page(output, page, config)
        return output

    @plugins.event_priority(-100)
    def on_post_build(self, config):
        """
        We build every language on its own directory.
        """

        # memorize locale search entries
        self.extend_search_entries(config)

        if self.building is False:
            self.building = True
        else:
            return

        # manually trigger with-pdf, see #110
        with_pdf_plugin = config["plugins"].get("with-pdf")
        if with_pdf_plugin:
            with_pdf_output_path = with_pdf_plugin.config["output_path"]
            with_pdf_plugin.on_post_build(config)

        # monkey patching mkdocs.utils.clean_directory to avoid
        # the site_dir to be cleaned up on each build() call
        from mkdocs import utils

        mkdocs_utils_clean_directory = utils.clean_directory
        utils.clean_directory = lambda x: x

        for locale in self.build_languages:
            if locale == self.current_language:
                continue
            self.current_language = locale
            log.info(f"Building '{locale}' documentation to directory: {config.site_dir}")
            # TODO: reconfigure config here? skip on_config?
            build(config)

            # manually trigger with-pdf for this locale, see #110
            if with_pdf_plugin:
                with_pdf_plugin.config["output_path"] = PurePath(
                    f"{locale}/{with_pdf_output_path}"
                ).as_posix()
                with_pdf_plugin.on_post_build(config)

        # rebuild and deduplicate the search index
        self.reconfigure_search_index(config)

        # remove monkey patching in case some other builds are triggered
        # on the same site (tests, ci...)
        utils.clean_directory = mkdocs_utils_clean_directory

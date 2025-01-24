import logging
import re
import sys
from pathlib import PurePath
from typing import Optional

from jinja2.ext import loopcontrols
from mkdocs import plugins
from mkdocs.commands.build import build
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from mkdocs_static_i18n import folder
from mkdocs_static_i18n.reconfigure import ExtendedPlugin
from mkdocs_static_i18n.utils import I18nLoggingFilter

log = get_plugin_logger(__name__)


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

        path_suffix = self.current_language if not self.is_default_language_build else ""

        log.info(
            f"Building '{self.current_language}' documentation to directory: "
            f"{PurePath(config.site_dir) / path_suffix}"
        )

        admonition_translations = self.current_language_config.admonition_translations or {}
        if len(admonition_translations) > 0 and (
            "markdown_extensions" not in config or "admonition" not in config["markdown_extensions"]
        ):
            log.warning(
                "admonition_translations used, but admonitions won't be rendered properly without 'admonition' in mkdocs.yml's markdown_extensions."
            )

        # reconfigure the mkdocs config
        config = self.reconfigure_mkdocs_config(config)

        # manually trigger with-pdf, to apply language specific overrides
        with_pdf_plugin = config.plugins.get("with-pdf")
        if with_pdf_plugin:
            config = with_pdf_plugin.on_config(config)

        return config

    @plugins.event_priority(-100)
    def on_files(self, files: Files, config: MkDocsConfig):
        """
        Construct the lang specific file tree which will be used to
        generate the navigation for the default site and per language.

        Note that each file's alternates are also built during this step.
        """
        i18n_files = self.reconfigure_files(files, config)
        # update the (cumulative) global alternates map which is
        # used by the sitemap.xml template
        self.i18n_files_per_language[self.current_language] = i18n_files.documentation_pages()
        return i18n_files

    @plugins.event_priority(-100)
    def on_nav(self, nav, config, files):
        """
        Translate i18n aware navigation to honor the 'nav_translations' option.
        """
        # folder structure, reconfigure navigation to remove language sections
        if self.config.docs_structure == "folder":
            nav = folder.reconfigure_navigation(self, nav)

        # reconfigure mkdocs-material blog navigation
        if self.config.reconfigure_material and "material/blog" in config.plugins:
            nav = self.reconfigure_material_blog(nav, config, files)

        homepage_suffix: str = "" if config.use_directory_urls else "index.html"

        class NavHelper:
            translated_items: int = 0
            homepage: Optional[Page] = nav.homepage
            expected_homepage_urls = [
                f"{self.current_language}/{homepage_suffix}",
                f"/{self.current_language}/{homepage_suffix}",
            ]

        # MkDocs resolves default/index.html, which isn't toplevel,
        # however the resolved path in the plugin is index.html
        if not config.use_directory_urls:
            NavHelper.expected_homepage_urls.append("index.html")

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
        with_pdf_plugin = config.plugins.get("with-pdf")
        if with_pdf_plugin:
            with_pdf_plugin.on_nav(i18n_nav, config, files)

        return i18n_nav

    def on_env(self, env, config, files):
        # Add extension to allow the "continue" clause in the sitemap template loops.
        env.add_extension(loopcontrols)

    @plugins.event_priority(50)
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
        context["i18n_alternates"] = self.i18n_files_per_language
        return context

    @plugins.event_priority(50)
    def on_page_markdown(self, markdown, page, config, files):
        """
        The page_markdown event is called after the page's markdown is loaded from file
        and can be used to alter the Markdown source text.

        Here we translate admonition and details titles.
        """
        admonition_translations = self.current_language_config.admonition_translations or {}

        marker = r"!{3}"  # Admonition marker
        if "pymdownx.details" in config["markdown_extensions"]:
            marker = r"(?:\?{3}\+?|!{3})"  # Admonition or Details marker

        # Copied from https://github.com/Python-Markdown/markdown/blob/master/markdown/extensions/admonition.py and modified for a single-line processing
        # Adapted to match the details extension as well
        RE = re.compile('^(' + marker + r' ?)([\w\-]+(?: +[\w\-]+)*)(?: +"(.*?)")? *$')

        def handle_admonition_translations(line):
            m = RE.match(line)
            if m:
                type = m.group(2)
                if (
                    m.group(3) is None or m.group(3).strip() == ''
                ) and type in admonition_translations:
                    title = admonition_translations[type]
                    line = m.group(1) + m.group(2) + f' "{title}"'
            return line

        out = []
        for line in markdown.splitlines():
            line = handle_admonition_translations(line)
            out.append(line)

        markdown = "\n".join(out)
        return markdown

    @plugins.event_priority(50)
    def on_page_context(self, context, page, config, nav):
        """
        Page context only applies to Page() objects.
        We add some metadata for users as well as some neat reconfiguration features.

        Overriden templates such as the sitemap.xml are not impacted by this method!
        """
        if isinstance(page, Page) and hasattr(page.file, "locale"):
            # export some useful i18n related variables on page context, see #75
            context["i18n_config"] = self.config
            context["i18n_file_locale"] = page.file.locale
            context["i18n_page_locale"] = self.current_language
            if self.config.reconfigure_material is True:
                context = self.reconfigure_page_context(context, page, config, nav)
        return context

    @plugins.event_priority(-100)
    def on_post_page(self, output, page, config):
        """
        Some plugins we control ourselves need this event.
        """
        # manually trigger with-pdf, see #110
        with_pdf_plugin = config.plugins.get("with-pdf")
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

        if self.building:
            return

        self.building = True

        # Block time logging for internal builds and filter reduntant MkDocs log
        build_logger = logging.getLogger("mkdocs.commands.build")
        i18n_filter = I18nLoggingFilter()
        i18n_filter.filtered_prefixes.add("Documentation built in")
        i18n_filter.filtered_prefixes.add("Building documentation to directory")
        build_logger.addFilter(i18n_filter)

        # manually trigger with-pdf, see #110
        with_pdf_plugin = config.plugins.get("with-pdf")
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
            # TODO: reconfigure config here? skip on_config?
            dirty = True if "--dirty" in sys.argv or "--dirtyreload" in sys.argv else False
            build(config, dirty=dirty)

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

        # Unblock time logging after internal builds
        build_logger.removeFilter(i18n_filter)

        self.building = False

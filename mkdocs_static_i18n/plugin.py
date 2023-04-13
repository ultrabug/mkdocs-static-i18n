import logging
from collections import defaultdict
from pathlib import PurePath

from jinja2.ext import loopcontrols
from mkdocs import plugins
from mkdocs.commands.build import build
from mkdocs.config.config_options import Choice, Type
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files

from mkdocs_static_i18n import reconfigure, suffix
from mkdocs_static_i18n.structure import Locale

try:
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


MKDOCS_THEMES = ["mkdocs", "readthedocs"]


class I18n(BasePlugin):
    """
    We use 'event_priority' to make sure that we are last plugin to be executed
    because we need to make sure that we react to other plugins' behavior
    properly.

    Current plugins we heard of and require that we control their order:
        - awesome-pages: this plugin should run before us
        - with-pdf: this plugin is triggerd by us on the appropriate on_* events
    """

    config_scheme = (
        (
            "docs_structure",
            Choice(["folder", "suffix"], default="suffix", required=False),
        ),
        ("fallback_to_default", Type(bool, default=True, required=False)),
        ("languages", Locale(dict, required=True)),
        ("material_alternate", Type(bool, default=True, required=False)),
        ("search_reconfigure", Type(bool, default=True, required=False)),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_languages = None
        self.build_languages = None
        self.building = False
        self.current_language = None
        self.default_language = None
        self.i18n_alternates = {}
        self.i18n_dest_uris = {}
        self.i18n_configs = {}
        self.i18n_files = defaultdict(list)
        self.material_alternates = None
        self.search_plugin = (None, None)
        self.site_dir = None

    @property
    def is_default_language_build(self):
        return self.current_language == self.default_language

    @plugins.event_priority(-100)
    def on_config(self, config: MkDocsConfig, **kwargs):
        """
        Enrich configuration with language specific knowledge.
        """
        # first execution, setup defaults
        if self.default_language is None:
            self.default_language = reconfigure.get_default_language(self.config)
        if self.current_language is None:
            self.current_language = self.default_language
        if self.all_languages is None:
            self.all_languages = [locale for locale in self.config["languages"].keys()]
        if self.build_languages is None:
            self.build_languages = reconfigure.get_languages_to_build(
                self.config, self.all_languages
            )
        return reconfigure.reconfigure_mkdocs_config(self, config)

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
        # because we build one language after the other, we need to rebuild
        # the alternates for each of them until the last built language
        # keep a reference of the i18n_files to build the alterntes for
        self.i18n_alternates[self.current_language] = i18n_files
        # reconfigure the alternates map by build language
        self.i18n_alternates = reconfigure.reconfigure_alternates(self)
        return i18n_files

    @plugins.event_priority(-100)
    def on_nav(self, nav, config, files):
        """
        Translate i18n aware navigation to honor the 'nav_translations' option.
        """
        i18n_nav = reconfigure.reconfigure_navigation(self, nav, config, files)

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
        context["i18n_current_language_config"] = self.config["languages"][
            self.current_language
        ]
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
        context = reconfigure.reconfigure_page_context(self, context, page, config, nav)
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
            log.info(
                f"Building '{locale}' documentation to directory: {config.site_dir}"
            )
            # TODO: reconfigure config here? skip on_config?
            build(config)

            # manually trigger with-pdf for this locale, see #110
            if with_pdf_plugin:
                with_pdf_plugin.config["output_path"] = PurePath(
                    f"{locale}/{with_pdf_output_path}"
                ).as_posix()
                with_pdf_plugin.on_post_build(config)

        # remove monkey patching in case some other builds are triggered
        # on the same site (tests, ci...)
        utils.clean_directory = mkdocs_utils_clean_directory

# Using i18 context variables

The plugin exports some useful i18n variables that you can access through the page context:

- `i18n_config`: the i18n plugin configuration
- `i18n_file_locale`: the locale of the source file used to build the page
- `i18n_page_locale`: the current rendering locale of the page

Those context [variables can be accessed using Jinja2 notation](https://jinja.palletsprojects.com/en/latest/templates/#variables), like `{{ i18n_page_locale }}` in your theme overrides.

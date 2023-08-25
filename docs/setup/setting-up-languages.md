# Setting up languages

This is where you define the languages you want to localize your site / documentation for. This configuration option is a **list of language definition key/value mappings** which allows you to localize almost every aspect of the MkDocs configuration, theme included!

For each language, you can for example localize (override) the MkDocs `site_name`, `site_description`, `copyright` etc... and even change (override) the theme options such as its color or logo!

!!! info
    The language `locale` selected as being the default one (`default: true`) will be the one built on the root path `/` of the site.

## Option: `languages`

Minimal example building only one language as the site root:

``` yaml
plugins:
  - i18n:
    languages:
        - locale: en
          name: English
          build: true
          default: true
```

### Per language build options:

|option|required|default|description|
|---|---|---|---|
|locale|yes||A 2-letter [ISO-639-1](https://en.wikipedia.org/wiki/ISO_639-1) language code (`en`) or [5-letter language code with added territory/region/country](https://www.mkdocs.org/user-guide/localizing-your-theme/#supported-locales) (`en_US`)|
|name|yes||The display name of the language|
|default|no|false|Specify that this locale is the default one, you **must** set it as `true` to at least one language!|
|build|no|true|Control whether to build or not the given language verion (useful when using the ENV! feature and speed up build testing)|
|link|no|`/<locale>/`|Used for the `mkdocs-material` language switcher. Absolute path used as the base of the language switcher|
|fixed_link|no||Used for the `mkdocs-material` language switcher. Fixed URL link used in the language switcher for this language|
|nav_translations|no||Key/value mapping used to [translate navigation items](localizing-navigation.md)|

Minimal example with two languages:

``` yaml
plugins:
  - i18n:
    languages:
        - locale: en
          name: English
          build: true
          default: true
        - locale: fr
          name: Français
          build: true
```

### Additional per language overrides options:

|option|required|default|description|
|---|---|---|---|
|copyright|no||Override the `copyright` option of `mkdocs.yml`|
|extra|no|true|Override the `extra` options of `mkdocs.yml`|
|nav|no|true|Override the `nav` option of `mkdocs.yml` to [specify a per-language navigation](localizing-navigation.md)|
|site_author|no|true|Override the `site_author` option of `mkdocs.yml`|
|site_description|no|true|Override the `site_description` option of `mkdocs.yml`|
|site_name|no|true|Override the `site_name` option of `mkdocs.yml`|
|site_url|no|true|Override the `site_url` option of `mkdocs.yml`|
|theme|no|true|Override the `theme` options of `mkdocs.yml`|

Overriding MkDocs options per language:

``` yaml
site_name: "MkDocs static i18n plugin documentation (en)"
site_description: "English description"

plugins:
  - i18n:
    languages:
      - locale: en
        default: true
        name: English
        build: true
      - locale: fr
        name: Français
        build: true
        site_name: "Documentation du plugin MkDocs static i18n (fr)"
        site_description: "Description Française"
        theme:
          palette:
            primary: red
```

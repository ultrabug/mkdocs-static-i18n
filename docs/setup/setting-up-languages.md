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

### Per language build options

|option|required|default|description|
|---|---|---|---|
|locale|yes||A 2-letter [ISO-639-1](https://en.wikipedia.org/wiki/ISO_639-1) language code (`en`) or [5-letter language code with added territory/region/country](https://www.mkdocs.org/user-guide/localizing-your-theme/#supported-locales) (`en_US`)|
|name|yes||The display name of the language|
|default|no|false|Specify that this locale is the default one, you **must** set it as `true` to at least one language!|
|build|no|true|Control whether to build or not the given language verion (useful when using the ENV! feature and speed up build testing)|
|link|no|`/<locale>/`|Used for the `mkdocs-material` language switcher. Absolute path used as the base of the language switcher|
|fixed_link|no||Used for the `mkdocs-material` language switcher. Fixed URL link used in the language switcher for this language|
|nav_translations|no||Key/value mapping used to [translate navigation items](localizing-navigation.md)|
|admonition_translations|no||Key/value mapping used to [translate admonitions](translating-content.md)|

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

### Additional per language overrides options

!!! warning
    Any option you override here **MUST** be set (even to its default) on its main `mkdocs.yml` section before being overriden on one or more languages.

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

Overriding MkDocs options per language is easy, here are some examples.

This example shows how to make the French (fr) version of the site use the `red` palette instead of the default `blue`:

``` yaml
site_name: "MkDocs static i18n plugin documentation (en)"
site_description: "English description"

theme:
  name: material
  palette:
    primary: blue

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

This example shows how to make the French (fr) light version of the site use the `red` palette instead of the default `blue` and the French (fr) dark version use the `pink` palette instead of `blue grey`:

``` yaml
site_name: "MkDocs static i18n plugin documentation (en)"
site_description: "English description"

theme:
  name: material
  palette:
    # Palette toggle for light mode
    - media: "(prefers-color-scheme: light)"
      primary: blue
      scheme: default
      toggle:
        icon: material/weather-sunny 
        name: Switch to dark mode
    # Palette toggle for dark mode
    - media: "(prefers-color-scheme: dark)"
      primary: blue grey
      scheme: slate
      toggle:
        icon: material/weather-night
        name: Switch to light mode

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
            # Palette toggle for light mode
            - media: "(prefers-color-scheme: light)"
              primary: red
              scheme: default
            # Palette toggle for dark mode
            - media: "(prefers-color-scheme: dark)"
              primary: pink
              scheme: slate
```

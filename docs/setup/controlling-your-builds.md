# Controlling your builds

Localized versions of your site / documentation are allowed to diverge from one to another depending on your docs structure and the fallback strategy you decide to adopt with the `fallback_to_default` option.

## Diverging from the default version

The localized (non default) language structure can have files which are not present in the default language version. This allows to have localized versions of your site diverging from the default one.


===  "Non diverging"
    ```
    docs_dir
    ├── assets
    │   └── image_non_localized.png
    ├── index.fr.md
    ├── index.en.md
    ├── topic1
    │   ├── index.en.md
    │   └── index.fr.md
    ```

    will build:

    ```
    site
    ├── 404.html
    ├── assets
    │   ├── image_non_localized.png

    [...]

    ├── fr
    │   ├── index.html
    │   ├── topic1
    │   │   └── index.html
    │   └── topic2
    │       └── index.html
    ├── index.html
    ├── search
    │   └── search_index.json
    ├── sitemap.xml
    ├── sitemap.xml.gz
    ├── topic1
    │   └── index.html
    └── topic2
        └── index.html
    ```

=== "Diverging"
    ```
    docs_dir
    ├── assets
    │   └── image_non_localized.png
    ├── index.fr.md
    ├── index.en.md
    ├── topic1
    │   ├── index.en.md
    │   └── index.fr.md
    └── french_only
    │   └── index.fr.md
    ```

    will build:

    ```
    site
    ├── 404.html
    ├── assets
    │   ├── image_non_localized.png

    [...]

    ├── fr
    │   ├── index.html
    │   ├── topic1
    │   │   └── index.html
    │   └── french_only     <-- only in the french /fr version
    │       └── index.html
    ├── index.html
    ├── search
    │   └── search_index.json
    ├── sitemap.xml
    ├── sitemap.xml.gz
    ├── topic1
    │   └── index.html
    ```


## Fallbacking to default

You can control whether you want the plugin to use (fallback to) the default language version of a page or resource when its localized version is missing from the docs structure.

### Option: `fallback_to_default`

|required|default|allowed values|
|---|---|---|
|no|true| true \| false|

``` yaml
plugins:
  - i18n:
    fallback_to_default: true
```

===  "fallback_to_default: true"
    ```
    docs_dir
    ├── assets
    │   └── image_non_localized.png
    ├── index.fr.md
    ├── index.en.md
    ├── topic1
    │   ├── index.en.md     <-- no french version
    ```

    will build:

    ```
    site
    ├── 404.html
    ├── assets
    │   ├── image_non_localized.png

    [...]

    ├── fr
    │   ├── index.html
    │   ├── topic1
    │   │   └── index.html      <-- built from the english version
    ├── index.html
    ├── search
    │   └── search_index.json
    ├── sitemap.xml
    ├── sitemap.xml.gz
    ├── topic1
    │   └── index.html
    ```

=== "fallback_to_default: false"
    ```
    docs_dir
    ├── assets
    │   └── image_non_localized.png
    ├── index.fr.md
    ├── index.en.md
    ├── topic1
    │   ├── index.en.md     <-- no french version
    ```

    will build:

    ```
    site
    ├── 404.html
    ├── assets
    │   ├── image_non_localized.png

    [...]

    ├── fr              <-- no topic1/ section on french version
    │   ├── index.html
    ├── index.html
    ├── search
    │   └── search_index.json
    ├── sitemap.xml
    ├── sitemap.xml.gz
    ├── topic1
    │   └── index.html
    ```

## Building only one specific locale

You can control if the plugin should build only one single locale. This would decrease build time during development. You can do it setting the `default` and `build` options of each language separately, or you can make use of the `build_only_locale` option and [*environment variables*](https://www.mkdocs.org/user-guide/configuration/#environment-variables) to select the built locale without modifying the `mkdocs.yml` file each time you switch languages.

### Option: `build_only_locale`

|required|default|allowed values|
|---|---|---|
|no|None|Language Code|

```yaml
plugins:
  - i18n:
    build_only_locale: !ENV [BUILD_ONLY_LOCALE]
```

Each operating system or terminal variant has a different way of setting and unsetting environmental variables:

```bash title="Linux (bash)"
export BUILD_ONLY_LOCALE=en
unset BUILD_ONLY_LOCALE
```

```powershell title="Windows Powershell"
$env:BUILD_ONLY_LOCALE="en"
$env:BUILD_ONLY_LOCALE=""
```

```batch title="Windows Command Prompt (cmd)"
set BUILD_ONLY_LOCALE=en
set BUILD_ONLY_LOCALE=
```

## Forcing default language into a subdirectory

By default, the default language is built at the root of the site (`/`), while other languages are built in their own subdirectories (e.g. `/en/`, `/fr/`). 

If you want to keep a consistent structure and have all languages, including the default one, in their own subdirectories, you can use the `force_default_in_subdirectory` option.

### Option: `force_default_in_subdirectory`

|required|default|allowed values|
|---|---|---|
|no|false| true \| false|

``` yaml
plugins:
  - i18n:
    force_default_in_subdirectory: true
```

===  "force_default_in_subdirectory: false (default)"
    ```
    docs_dir
    ├── index.fr.md
    ├── index.en.md (default language)
    ```

    will build:

    ```
    site
    ├── fr
    │   └── index.html
    └── index.html  # from the default language
    ```

=== "force_default_in_subdirectory: true"
    ```
    docs_dir
    ├── index.fr.md
    ├── index.en.md (default language)
    ```

    will build:

    ```
    site
    ├── fr
    │   └── index.html
    ├── en           # default language is now in subdirectory
    │   └── index.html
    ```

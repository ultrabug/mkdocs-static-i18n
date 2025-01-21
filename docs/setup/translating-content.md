# Translating content

**Focus on translating your content**, not on updating all the links and references to your files!

Let `mkdocs-static-i18n` do the heavy lifting of dynamically localizing your assets and just reference everything without their localized extension.

Since the generated `site` files have their localization extension removed during the build process, you **must** reference them in your markdown source without it (this includes links to `.md` files)!

This simple docs structure:

```
docs
├── image.en.png
├── image.fr.png
├── index.fr.md
├── index.md
```

Will generate this site tree:

```
site
├── fr
│   ├── image.png
│   ├── index.html
├── image.png
├── index.html
```

Which means that the `image.png` and its `fr/image.png` localized counterpart can be referenced the same way as `![my image](image.png)` on both `index.md` and `index.fr.md` when using the `suffix` docs structure.

It works the same for the `folder` structure!

!!! tip
    You may find useful to inform users that some pages are not translated (yet) by [injecting content on an announcement block](https://github.com/ultrabug/mkdocs-static-i18n/issues/276#issuecomment-1785900709) when a page is displayed using its fallback language and thus missing a translation.

## Translating admonitions

This sub-option is a key/value mapping set per language and allows you to translate [admonition](https://python-markdown.github.io/extensions/admonition/) titles which don't have an explicit title defined.

Also, this configuration will apply to [PyMdown Details Extension][details], if the extension is enabled.

[details]: https://facelessuser.github.io/pymdown-extensions/extensions/details/

### Language Sub-Option: `admonition_translations`

This example overrides admonition titles of the French version of the site.

``` yaml
plugins:
  - i18n:
    languages:
      - locale: en
        default: true
        name: English
      - locale: fr
        name: Français
        admonition_translations:
          - tip: Conseil
          - warning: Avertissement

markdown_extensions:
  - admonition
  - pymdownx.details
```

and translates French markdowns:

=== "admonitions"
    From:

    ```
    !!! tip

        Bonjour le monde
    ```

    to:

    ```
    !!! tip "Conseil"

        Bonjour le monde
    ```

=== "details"
    From:

    ```
    ??? tip

        Bonjour le monde
    ```

    to:

    ```
    ??? tip "Conseil"

        Bonjour le monde
    ```

=== "details (open)"
    From:

    ```
    ???+ tip

        Bonjour le monde
    ```

    to:

    ```
    ???+ tip "Conseil"

        Bonjour le monde
    ```

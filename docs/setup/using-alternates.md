# Using i18n alternates

The `mkdocs-static-i18n` plugin keeps track of every page alternate and makes this information available to template builders:

- `i18n_build_languages`: list of the language locales with `build: true`
- `i18n_current_language_config`: locale specific configuration of the language currently building
- `i18n_current_language`: locale of the language currently building
- `i18n_alternates`: locale/Files (from mkdocs.structure.files) mapping used to build the sitemap.xml

## Localized sitemap

Since version 0.32 the plugin provides a template that will generate automatically an alternate aware `sitemap.xml` so that your localized content is made available to search engines!

Check out the [localization aware sitemap.xml](/mkdocs-static-i18n/sitemap.xml) of this documentation!

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
    <url>
        <loc>https://ultrabug.github.io/mkdocs-static-i18n/</loc>
        <lastmod>2023-08-25</lastmod>
        <changefreq>daily</changefreq>
        <xhtml:link rel="alternate" hreflang="en" href="https://ultrabug.github.io/mkdocs-static-i18n/"/>
        <xhtml:link rel="alternate" hreflang="de" href="https://ultrabug.github.io/mkdocs-static-i18n/de/"/>
        <xhtml:link rel="alternate" hreflang="fr" href="https://ultrabug.github.io/mkdocs-static-i18n/fr/"/>
    </url>
    <url>
        <loc>https://ultrabug.github.io/mkdocs-static-i18n/getting-started/installation/</loc>
        <lastmod>2023-08-25</lastmod>
        <changefreq>daily</changefreq>
        <xhtml:link rel="alternate" hreflang="en" href="https://ultrabug.github.io/mkdocs-static-i18n/getting-started/installation/"/>
        <xhtml:link rel="alternate" hreflang="de" href="https://ultrabug.github.io/mkdocs-static-i18n/de/getting-started/installation/"/>
        <xhtml:link rel="alternate" hreflang="fr" href="https://ultrabug.github.io/mkdocs-static-i18n/fr/getting-started/installation/"/>
    </url>
    <url>
        <loc>https://ultrabug.github.io/mkdocs-static-i18n/getting-started/philosophy/</loc>
        <lastmod>2023-08-25</lastmod>
        <changefreq>daily</changefreq>
        <xhtml:link rel="alternate" hreflang="en" href="https://ultrabug.github.io/mkdocs-static-i18n/getting-started/philosophy/"/>
        <xhtml:link rel="alternate" hreflang="de" href="https://ultrabug.github.io/mkdocs-static-i18n/de/getting-started/philosophy/"/>
        <xhtml:link rel="alternate" hreflang="fr" href="https://ultrabug.github.io/mkdocs-static-i18n/fr/getting-started/philosophy/"/>
    </url>

    ...

</urlset>
```

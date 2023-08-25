# Setting up search

When using the `search` or `material/search` plugin, the `reconfigure_search` option allows you to control whether you want the plugin to remove duplicate content from your search results.

This is especially useful if you have non-localized content along with the `fallback_to_default: true` option set as some of your language content will be copied over to language specific paths and added to the search results (which would cause duplicate results).

## Option: `reconfigure_search`

|required|default|allowed values|
|---|---|---|
|no|true| true \| false|

``` yaml
plugins:
  - i18n:
    reconfigure_search: true
```

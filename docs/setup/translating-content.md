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

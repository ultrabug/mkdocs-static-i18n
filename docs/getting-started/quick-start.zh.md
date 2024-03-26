# 快速开始

!!! Warning
    本文档适用于 `mkdocs-static-i18n` **1.0.0 版本及以上**。
    如果你在使用0.56或更旧的版本请看[这份文档](https://github.com/ultrabug/mkdocs-static-i18n/tree/0.56#readme).


当[安装](installation.md)完插件后按照以下步骤开始。

## 选择您的本地化文档架构

该插件允许您选择如何管理你的本地化页面文档。


- 使用 `suffix` 文档结构 (默认), 你可以在你的文件后面加后缀 `.<language>.<extension>` (类似 `index.zh.md`)。
- 使用 `folder` 文档结构, 你将为你的每一种语言的文档创建一个文件夹 (类似 `zh/` 和 `en/` 等)，并将您的本地化页面放在这些文件夹里面。

以下是两种结构的示例，您可以自行决定选择哪一种，构建输出的结果一致。

### 后缀文件结构 (默认)

```
./docs_suffix_structure
├── assets
│   └── image_non_localized.png
├── image.en.png
├── image.zh.png
├── index.zh.md
├── index.en.md
├── topic1
│   ├── index.en.md
│   └── index.zh.md
└── topic2
│   ├── index.en.md
│   └── index.zh.md
```

### 文件夹文件结构

```
./docs_folder_structure
├── assets
│   └── image_non_localized.png
├── en
│   ├── image.png
│   ├── index.md
│   ├── topic1
│   │   └── index.md
│   └── topic2
│       └── index.md
└── zh
    ├── image.png
    ├── index.md
    ├── topic1
    │   └── index.md
    └── topic2
        └── index.md
```

## 在您的mkdocs.yml文件中配置该插件

一旦您选择使用哪种结构（这里我们选择`suffix`结构），就可以添加插件并进行最低要求的配置，以支持您所期望的语言，同时**选择默认语言**。

不要担心缺少非默认语言 (此处为`zh`) 的页面: 默认情况下，它们将使用默认版本 (`en`) (您可以使用`fallback_to_default`选项配置)。

```yaml
plugins:
  - i18n:
      docs_structure: suffix
      languages:
        - locale: en
          default: true
          name: English
          build: true
        - locale: zh
          name: zhançais
          build: true
```

## 构建和测试您本地化后的网站

恭喜，您已经可以看到您的本地化网站，因为该插件将为每种语言生成一个URL路径:

- 使用默认 (`en`) 语言URL会显示根目录 `/` 。
- 本地化后的 (`zh`) 汉语路径URL会显示为 `/zh/` 中。

```bash
$ mkdocs serve
```
该插件将生成如下的网站结构：

```
site
├── 404.html
├── assets
│   ├── image_non_localized.png

[...]

├── zh
│   ├── image.png
│   ├── index.html
│   ├── topic1
│   │   └── index.html
│   └── topic2
│       └── index.html
├── image.png
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

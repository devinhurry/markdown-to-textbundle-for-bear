# Markdown notes to bear notes text bundle

[中文](README_zh.md) [日本語](README_jp.md)

## Environment
- python 3 required
- pip install -r requirements.txt

## Summary
Takes as input the name of a folder containing markdown files
and their associated images and attachments, and creates a `.textbundle` for each markdown file.
Each `.textbundle` also contains any images or attachments used by the markdown file.
It can handle both markdown and images/attachments held in subfolders.


## Usage
1. `python md-to-bundle.py your-markdown-folder`
2. use subfolder names as tags: `python md-to-bundle.py your-markdown-folder --tags`


The exported `textbundle` files will be in `your-markdown-folder-export`

# Features
- Copy attachments to the text bundle
- Support obsidian's `![[file]]` format
- Convert `[](markdown.md)` to `[[markdown]]`
- Insert file name(or title in front matter) as title to first line of document (because bear takes first line as title by default)
- Preserve modification time (take modify time from front matter if has one)
- Optionally use subfolder name as tags (with `--tags`)
- Retrieve information from front matter
- Tested apps
    - Obsidian
    - Joplin (exported as Markdown or Markdown + Front Matter)
    - Upnote (exported as Markdown)
        - Use the `--tags` option in order to capture Upnote 'Notebooks' as nested tags

# Markdown notes to bear notes text bundle

[中文](README_zh.md) [日本語](README_jp.md)

## Environment
- python 3 required
- pip install -r requirements.txt

## Usage
1. `python md-to-bundle.py your-markdown-folder`
2. use subfolder names as tags: `python md-to-bundle.py your-markdown-folder --tags`

exported file will be in `your-markdown-folder-export`

# Features
- Copy attachments to the text bundle
- Support obsidian's `![[file]]` format
- Preserve modification time
- Optionally use subfolder names as tags (with `--tags`)
- Retrieve information from front matter
- Tested apps
    - Obsidian
    - Joplin(Markdown and Markdown + Front Matter)
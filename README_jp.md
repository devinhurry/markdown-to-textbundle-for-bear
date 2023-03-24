# MarkdownノートをBearノートのテキストバンドルに変換する
## 環境
- Python 3が必要です 
- `pip install -r requirements.txt`を実行して依存関係をインストールしてください。
## 使い方 
1. `python md-to-bundle.py your-markdown-folder`を実行します。 
2. サブフォルダ名をタグとして使用する場合: `python md-to-bundle.py your-markdown-folder --tags`

エクスポートされたファイルは`your-markdown-folder-export`に保存されます。
## 機能
- 添付ファイルをテキストバンドルにコピーする 
- Obsidianの`![[file]]`フォーマットをサポート
- 変更日時を保持する 
- サブフォルダ名をオプションでタグとして使用できる(`--tags`オプションで指定)
- front matterから情報を取得する 
- テスト済みアプリケーション
    - Obsidian
    - Joplin(MarkdownとMarkdown + Front Matter)
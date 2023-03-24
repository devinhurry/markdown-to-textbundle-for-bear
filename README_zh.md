# Markdown笔记转换成Bear Notes文本包
## 环境
- 需要Python 3
- 运行pip install -r requirements.txt 安装依赖
## 使用方法 
1. 运行`python md-to-bundle.py 你的Markdown文件夹路径` 
2. 使用子文件夹名称作为标签：`python md-to-bundle.py 你的Markdown文件夹路径 --tags`

导出的文件将在`你的Markdown文件夹路径-export`目录中。
# 功能
- 将附件复制到文本包中 
- 支持Obsidian的`![[file]]`格式
- 保留修改时间 
- 可选地使用子文件夹名称作为标签（使用`--tags`选项）
- 从front matter中获取信息 
- 测试过的应用程序
    - Obsidian
    - Joplin（Markdown和Markdown + Front Matter）
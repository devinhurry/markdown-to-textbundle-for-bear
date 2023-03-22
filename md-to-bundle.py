import os
import re
import shutil
import sys
import urllib.parse
import argparse


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
    

def write_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def get_files(dir_path):
    files = []
    for root, dirs, file_names in os.walk(dir_path):
        for file_name in file_names:
            file_path = os.path.join(root, file_name)
            files.append(file_path)
    return files


def md_to_bundle(md_path, add_tag, relative_dir, export_dir):
    content = read_file(md_path)
    if add_tag and len(relative_dir) > 0:
        # insert tag into second line
        content = content.replace('\n', '\n#{}\n '.format(relative_dir), 1)
    # find patter like this ![somefile](somefile)
    file_pattern1 = re.compile(r'\!\[.*?\]\((.*?)\)')
    # find patter like this ![[somefile]]
    file_pattern2 = re.compile(r'\!\[\[(.*?)\]\]')
    file_names1 = file_pattern1.findall(content)
    file_names2 = file_pattern2.findall(content)

    # create textbundle dir
    basename = os.path.basename(md_path)
    bundle_path = os.path.join(export_dir, basename.replace('.md', '.textbundle'))
    if not os.path.exists(bundle_path):
        os.makedirs(bundle_path)

    # create assets dir
    assetsPath = os.path.join(bundle_path, 'assets')
    if not os.path.exists(assetsPath):
        os.makedirs(assetsPath)

    # create info.json
    info_path = os.path.join(bundle_path, 'info.json')
    info_content = '{"type":"net.daringfireball.markdown","version":2}'
    write_file(info_path, info_content)

    # create text.md 
    markdown_content = content
    for file_name in file_names1:
        if file_name.startswith('http'):
            continue

        if file_name == '':
            print('filename is empty {}'.format(md_path))
            continue
        # replace path to assets/file_name
        quotedfile_name = urllib.parse.quote(os.path.basename(file_name))
        markdown_content = markdown_content.replace(file_name, os.path.join('assets', quotedfile_name))
        # copy file to textbundle/assets
        file_name = urllib.parse.unquote(file_name)
        filePath = os.path.join(os.path.dirname(md_path), file_name)
        if os.path.exists(filePath):
            shutil.copyfile(filePath, os.path.join(assetsPath, os.path.basename(file_name)))
    for file_name in file_names2:
        if file_name == '':
            print('filename is empty {}'.format(md_path))
            continue
        quotedfile_name = urllib.parse.quote(os.path.basename(file_name))
        # replace ![[file]] to ![](assets/file)
        markdown_content = markdown_content.replace('![[{}]]'.format(file_name), '[]({})'.format(os.path.join('assets', quotedfile_name)))
        # copy file to textbundle/assets
        file_name = urllib.parse.unquote(file_name)
        filePath = os.path.join(os.path.dirname(md_path), file_name)
        if os.path.exists(filePath):
            shutil.copyfile(filePath, os.path.join(assetsPath, os.path.basename(file_name)))

    markdownContentPath = os.path.join(bundle_path, 'text.md')
    write_file(markdownContentPath, markdown_content)

    # preserve creat time and modify time
    src_ctime = os.path.getctime(md_path)
    src_mtime = os.path.getmtime(md_path)
    os.utime(bundle_path, (src_ctime, src_mtime))

def main():
    # get named arg --tags
    add_tag = False
    argparser = argparse.ArgumentParser()
    argparser.add_argument("markdown_notes_dir", help="markdown notes dir")
    argparser.add_argument('--tags', action='store_true', help='add tags to bear')
    args = argparser.parse_args()
    if args.tags:
        add_tag = True

    markdown_notes_dir = args.markdown_notes_dir
    print('Using markdown_notes_dir: {}'.format(markdown_notes_dir))

    # export_dir is the same level with markdown_notes_dir and append '-export'
    export_dir = os.path.join(os.path.dirname(markdown_notes_dir), os.path.basename(markdown_notes_dir) + '-export')
    if os.path.exists(export_dir):
        # rm dir
        shutil.rmtree(export_dir)
    os.makedirs(export_dir)

    # trim the last separator
    markdown_notes_dir = markdown_notes_dir.rstrip(os.sep)
    files = get_files(markdown_notes_dir)
    for file in files:
        if file.endswith(".md"):
            # get relative dir
            relative_dir = os.path.dirname(file).replace(markdown_notes_dir, '')
            tag = relative_dir.lstrip(os.sep)
            md_to_bundle(file, add_tag, tag, export_dir)

if __name__ == '__main__':
    main()


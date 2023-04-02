import datetime
import os
import re
import shutil
import urllib.parse
import argparse
import yaml


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


def parse_front_matter(content):
    front_matter = None
    end_index = 0
    if content.startswith('---'):
        end_index = content.find('---', 3)
        if end_index > 0:
            front_matter_content = content[3:end_index]
            # parse as yaml
            front_matter = yaml.load(
                front_matter_content, Loader=yaml.FullLoader)
            end_index += 3

    return front_matter, end_index


def md_to_bundle(md_path, add_tag, tag, export_dir):
    content = read_file(md_path)
    front_matter, end_index = parse_front_matter(content)
    basename = os.path.basename(md_path)

    # Dealing with tags
    if front_matter is not None:
        tags = front_matter.get('tags', [])
    else:
        tags = []
    if isinstance(tags, str):
        if tags == '':
            tags = []
        else:
            tags = [tags]
    if add_tag and len(tag) > 0:
        tags.append(tag)
    if len(tags) > 0:
        # escape
        escaped_tags = []
        for t in tags:
            escaped_tags.append(''.join(c for c in t if re.match(r'\w', c)))
        fm_tags_str = ' #'.join(escaped_tags)
        fm_tags_str = fm_tags_str.lstrip()
        # insert tag in end of file
        content = content + '\n#{}'.format(fm_tags_str)

    # Find all links in the markdown
    # find patter like this ![somefile](somefile)
    links_pattern = re.compile(r'(\[.*?\]\((.*?)\))')
    # find patter like this ![[somefile]]
    wiki_links_pattern = re.compile(r'(\!\[\[(.*?)\]\])')
    links = links_pattern.finditer(content)
    wiki_links = wiki_links_pattern.finditer(content)

    # Because bear use document first line as title by default,
    # we need to insert title in front of markdown content if the first line is not title
    md_title = os.path.splitext(basename)[0]
    if front_matter is not None and 'title' in front_matter:
        md_title = front_matter['title']
    # find the title of content(first no empty line) after front matter(end_index)
    lines = content[end_index:].splitlines()
    line = ""
    # print("end index is {}".format(end_index))
    for line in lines:
        if line.strip():
            line = line.strip()
            break
    # remove #+\s
    line = re.sub(r'^#+\s', '', line)
    if line == "":
        content = content + '\n#{}'.format(md_title)
    elif line != md_title:
        # insert title in front of content
        if end_index == 0:
            content = '# {}\n'.format(md_title) + content
        else:
            content = content[:end_index] + \
                '\n# {}\n'.format(md_title) + content[end_index:]

    # Create textbundle dir
    bundle_path = os.path.join(
        export_dir, basename.replace('.md', '.textbundle'))
    if not os.path.exists(bundle_path):
        os.makedirs(bundle_path)

    # Create assets dir
    assetsPath = os.path.join(bundle_path, 'assets')
    if not os.path.exists(assetsPath):
        os.makedirs(assetsPath)

    # Create info.json
    info_path = os.path.join(bundle_path, 'info.json')
    info_content = '{"type":"net.daringfireball.markdown","version":2}'
    write_file(info_path, info_content)

    # Create text.md
    markdown_content = content

    # Many cases included
    # Case 1: ![](./markdown file.md) => [[markdown file]] [](./markdown file.md) => [[markdown file]]
    # Case 2: ![[markdown file]] => [[markdown file]]
    # Othercase: ![](./media file.png) => ![](./assets/media file.png)
    #           ![[media file.png/jpeg/pdf...so on]] => ![](./assets/media file.png)

    def copy_and_replace_assets(full_link, original_link, is_wiki_link):
        nonlocal markdown_content, assetsPath
        # replace path to assets/file_name
        if original_link == '':
            return
        if original_link.startswith('#'):
            return
        if original_link.startswith('http://') or original_link.startswith('https://'):
            return
        # if starts with [a-zA-Z]+:, return
        if re.match(r'^[a-zA-Z\-0-9]+:', original_link):
            return
        unquoted_filename = urllib.parse.unquote(original_link)

        # if it is a markdown file, replace it with wiki link
        # Case 1: ![](./markdown file.md) => [[markdown file]] [](./markdown file.md) => [[markdown file]]
        basename = os.path.basename(unquoted_filename)
        ext = os.path.splitext(basename)[1]
        title = os.path.splitext(basename)[0]
        if ext == '.md':
            # reg replace ![.*](./markdown file.md) to ![[markdown file]]
            escaped_file_name = re.escape(original_link)
            markdown_content = re.sub(
                rf'!\[.*\]\({escaped_file_name}\)', '[[{}]]'.format(title), markdown_content)
            markdown_content = re.sub(
                rf'\[.*\]\({escaped_file_name}\)', '[[{}]]'.format(title), markdown_content)
            return

        quotedfile_name = urllib.parse.quote(
            os.path.basename(unquoted_filename))

        true_file_name = urllib.parse.unquote(original_link)
        file_path = os.path.join(os.path.dirname(md_path), true_file_name)

        # Case 2: ![[markdown file]] => [[markdown file]]
        if is_wiki_link and ext == "" and not os.path.exists(file_path) and os.path.exists(file_path + '.md'):
            source_pattern = '![[{}]]'
            dest_pattern = '[[{}]]'
            markdown_content = markdown_content.replace(source_pattern.format(original_link),
                                                        dest_pattern.format(unquoted_filename))
            return

        # Othercase: ![](./media file.png) => ![](./assets/media file.png)
        #            ![[media file.png/jpeg/pdf...so on]] => ![](./assets/media file.png)
        # copy file to textbundle/assets
        if os.path.exists(file_path):

            if is_wiki_link:
                source_pattern = '![[{}]]'
                dest_pattern = '![]({})'
            else:
                source_pattern = '{}'
                dest_pattern = '{}'
            markdown_content = markdown_content.replace(source_pattern.format(original_link),
                                                        dest_pattern.format(os.path.join('assets', quotedfile_name)))
            shutil.copyfile(file_path, os.path.join(
                assetsPath, os.path.basename(true_file_name)))
        else:
            # This case ![](media file.png) or ![[media file.png]] is not exist
            print('link not exist: {} in markdown file {}'.format(
                full_link, md_path))
            pass

    # Copy files to assets dir and replace path
    for matches in links:
        copy_and_replace_assets(matches.group(
            1), matches.group(2), is_wiki_link=False)

    # Copy files to assets dir and replace path (for ![[file]])
    for matches in wiki_links:
        copy_and_replace_assets(matches.group(
            1), matches.group(2), is_wiki_link=True)

    markdownContentPath = os.path.join(bundle_path, 'text.md')
    write_file(markdownContentPath, markdown_content)

    # Preserve creat time and modify time
    has_front_matter_time = False
    if front_matter is not None:
        ctime = front_matter.get('created', None)
        mtime = front_matter.get('updated', None)
        if ctime is None:
            ctime = mtime
        if mtime is None:
            mtime = ctime
        # if is datetime
        if isinstance(ctime, datetime.datetime) and isinstance(mtime, datetime.datetime):
            os.utime(bundle_path, (ctime.timestamp(), mtime.timestamp()))
            has_front_matter_time = True
    if not has_front_matter_time:
        src_ctime = os.path.getctime(md_path)
        src_mtime = os.path.getmtime(md_path)
        os.utime(bundle_path, (src_ctime, src_mtime))


def main():
    # get named arg --tags
    add_tag = False
    argparser = argparse.ArgumentParser()
    argparser.add_argument("markdown_notes_dir", help="markdown notes dir")
    argparser.add_argument('--tags', action='store_true',
                           help='add tags to bear')
    args = argparser.parse_args()
    if args.tags:
        add_tag = True

    markdown_notes_dir = args.markdown_notes_dir
    markdown_notes_dir = markdown_notes_dir.rstrip(os.sep)
    print('Using markdown_notes_dir: {}'.format(markdown_notes_dir))

    # export_dir is the same level with markdown_notes_dir and append '-export'
    export_dir = os.path.join(os.path.dirname(
        markdown_notes_dir), os.path.basename(markdown_notes_dir) + '-export')

    # Doing clean
    if os.path.exists(export_dir):
        # rm dir
        shutil.rmtree(export_dir)
    os.makedirs(export_dir)

    # Find all markdown files
    # trim the last separator
    markdown_notes_dir = markdown_notes_dir.rstrip(os.sep)
    files = get_files(markdown_notes_dir)

    count = 0
    for file in files:
        if file.endswith(".md"):
            # get relative dir
            relative_dir = os.path.dirname(
                file).replace(markdown_notes_dir, '')
            tag = relative_dir.lstrip(os.sep)
            md_to_bundle(file, add_tag, tag, export_dir)
            count += 1
    print('Exported to {}, Total count: {}'.format(export_dir, count))


if __name__ == '__main__':
    main()

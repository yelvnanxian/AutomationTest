#!/usr/bin/env python3
"""作用：批量移除第一方文本文件中的旧作者信息并补充文件用途说明。"""

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_SUFFIXES = {'.py', '.sh', '.conf', '.ini', '.md', '.txt', '.yml', '.yaml', '.xml', '.java'}
SUPPORTED_NAMES = {'.gitignore'}
EXCLUDED_PREFIXES = (
    'common/aliyun_mns/mns/',
    'common/encrypt_tools/gmssl/',
    'common/java/lib/',
)
AUTHOR_LINE = re.compile(
    r'(?i)^\s*(?:#|//|<!--).*?(?:作者|@author|created\s+by|'
    r'copyright\s+(?:\(c\)\s*)?[^<]*).*?(?:-->)?\s*$'
)
CODING_LINE = re.compile(r'^\s*#.*coding[:=]\s*[-\w.]+')
LEGACY_METADATA_LINE = re.compile(
    r'^\s*#\s*(?:$|创建时间\b.*|@(?:Time|created|last-modified|description)\b.*|'
    r'[A-Za-z_][\w.-]*\.py\s*)$',
    re.IGNORECASE,
)


def tracked_text_files():
    output = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
        cwd=ROOT,
    )
    for raw_path in output.decode('utf-8').split('\0'):
        if not raw_path:
            continue
        if raw_path.startswith(EXCLUDED_PREFIXES):
            continue
        path = ROOT / raw_path
        if not path.is_file():
            continue
        if path.suffix.lower() in SUPPORTED_SUFFIXES or path.name in SUPPORTED_NAMES:
            yield path


def human_name(path):
    name = path.stem.replace('_', ' ').strip()
    return name or path.parent.name


def purpose_for(path):
    relative = path.relative_to(ROOT)
    relative_text = relative.as_posix()
    name = path.name
    stem = human_name(path)

    if name == '__init__.py':
        package_name = relative.parent.as_posix().replace('/', '.') or '项目根'
        return '初始化%s包并定义其模块边界。' % package_name
    if path.suffix == '.py' and name.startswith('test_'):
        return '定义%s相关的自动化测试用例。' % stem.replace('test ', '')
    if name.startswith('run_'):
        return '提供%s流程的命令行执行入口。' % stem.replace('run ', '')
    if name.startswith('generate_') and 'report' in name:
        return '生成并启动%s对应的Allure测试报告。' % stem.replace('generate ', '')
    if name.startswith('read_') or 'read_config' in name:
        return '读取并解析%s所需的配置。' % stem.replace('read ', '')
    if name.endswith('Elements.py') or '/elements/' in relative_text:
        return '定义%s页面或界面的元素定位信息。' % stem
    if name.endswith('Page.py') or '/pages/' in relative_text:
        return '封装%s页面的用户操作和状态读取。' % stem
    if name.endswith('_client.py') or name.endswith('Client.py'):
        return '封装%s客户端的连接和访问能力。' % stem
    if name.endswith('_config.py') or name.endswith('Config.py') or relative_text.startswith('pojo/'):
        return '定义或承载%s相关的数据结构。' % stem
    if relative_text.startswith('init/'):
        return '执行%s相关的运行前初始化。' % stem
    if relative_text.startswith('cases/performance/'):
        return '定义%s相关的性能测试任务。' % stem
    if relative_text.startswith('common/') or name.lower().endswith('tool.py'):
        return '提供%s相关的通用工具能力。' % stem
    if relative_text.startswith('base/'):
        return '提供%s相关的基础封装。' % stem
    if relative_text.startswith('models/'):
        return '定义%s相关的持久化模型。' % stem
    if relative_text.startswith('common_projects/'):
        return '封装%s相关的项目公共业务能力。' % stem
    if path.suffix in {'.conf', '.ini'}:
        return '配置%s相关的运行参数。' % stem
    if path.suffix == '.sh':
        return '提供%s相关的Shell启动命令。' % stem
    if path.suffix in {'.yml', '.yaml'}:
        return '定义%s相关的自动化工作流配置。' % stem
    if path.suffix == '.xml':
        return '定义%s相关的XML构建或配置内容。' % stem
    if path.suffix == '.md':
        return '说明%s相关的使用方式和设计信息。' % stem
    if path.suffix == '.txt':
        return '记录%s相关的依赖或文本配置。' % stem
    if path.name == '.gitignore':
        return '定义Git版本控制需要忽略的文件和目录。'
    return '提供%s模块相关功能。' % stem


def remove_author_lines(lines):
    return [line for line in lines if not AUTHOR_LINE.match(line)]


def remove_legacy_header_metadata(lines):
    return [
        line for index, line in enumerate(lines)
        if index >= 12 or not LEGACY_METADATA_LINE.match(line)
    ]


def insert_after_prefix(lines, prefix_count, comment_lines):
    while prefix_count < len(lines) and not lines[prefix_count].strip():
        prefix_count += 1
    return lines[:prefix_count] + comment_lines + [''] + lines[prefix_count:]


def update_python(lines, purpose):
    if any('作用：' in line for line in lines[:12]):
        return lines
    prefix_count = 0
    if lines and lines[0].startswith('#!'):
        prefix_count = 1
    if prefix_count < len(lines) and CODING_LINE.match(lines[prefix_count]):
        prefix_count += 1
    elif prefix_count == 0 and len(lines) > 1 and CODING_LINE.match(lines[1]):
        prefix_count = 2
    return insert_after_prefix(lines, prefix_count, ['"""作用：%s"""' % purpose])


def update_shell(lines, purpose):
    if any('作用：' in line for line in lines[:8]):
        return lines
    prefix_count = 1 if lines and lines[0].startswith('#!') else 0
    return insert_after_prefix(lines, prefix_count, ['# 作用：%s' % purpose])


def update_xml(lines, purpose):
    if any('作用：' in line for line in lines[:8]):
        return lines
    prefix_count = 1 if lines and lines[0].lstrip().startswith('<?xml') else 0
    return insert_after_prefix(lines, prefix_count, ['<!-- 作用：%s -->' % purpose])


def update_markdown(lines, purpose):
    if any('作用：' in line for line in lines[:8]):
        return lines
    return insert_after_prefix(lines, 0, ['<!-- 作用：%s -->' % purpose])


def update_commentable(lines, purpose, marker):
    if any('作用：' in line for line in lines[:8]):
        return lines
    return insert_after_prefix(lines, 0, ['%s 作用：%s' % (marker, purpose)])


def update_file(path):
    original = path.read_text(encoding='utf-8-sig')
    had_trailing_newline = original.endswith('\n')
    lines = remove_author_lines(original.splitlines())
    lines = remove_legacy_header_metadata(lines)
    purpose = purpose_for(path)

    if path.suffix == '.py':
        lines = update_python(lines, purpose)
    elif path.suffix == '.sh' or path.name == '.gitignore':
        lines = update_shell(lines, purpose)
    elif path.suffix == '.xml':
        lines = update_xml(lines, purpose)
    elif path.suffix == '.md':
        lines = update_markdown(lines, purpose)
    elif path.suffix == '.java':
        lines = update_commentable(lines, purpose, '//')
    else:
        lines = update_commentable(lines, purpose, '#')

    lines = [line.rstrip() for line in lines]
    while lines and not lines[-1]:
        lines.pop()

    updated = '\n'.join(lines)
    if had_trailing_newline or updated:
        updated += '\n'
    if updated != original:
        path.write_text(updated, encoding='utf-8')
        return True
    return False


def main():
    updated_files = []
    for path in tracked_text_files():
        try:
            if update_file(path):
                updated_files.append(path.relative_to(ROOT).as_posix())
        except UnicodeDecodeError:
            continue
    print('已更新%s个文件。' % len(updated_files))
    return 0


if __name__ == '__main__':
    sys.exit(main())

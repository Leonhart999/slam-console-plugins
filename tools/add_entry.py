#!/usr/bin/env python3
"""Add or replace plugin entries in index.json.

    python3 tools/add_entry.py <id>-<version>.entry.json [...] [--check-url]

An entry file is written by `package.py` in a plugin's repository (robot_console_plugin/package.py). The entry
replaces the one with the same id (the index keeps one version per plugin: the newest). With --check-url the zip
is downloaded and its size and SHA-256 compared with the entry. The checks mirror the console's
(robot_console/plugin_market.py check_entry), so the console will not skip an entry this script accepts.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(HERE, 'index.json')
ID_RE = re.compile(r'^[a-z][a-z0-9_]{1,39}$')
REQ_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*(?:\[[A-Za-z0-9._-]+(?:,[A-Za-z0-9._-]+)*\])?'
                    r'(?:\s*(?:===|==|!=|~=|<=|>=|<|>)\s*[A-Za-z0-9.*+!_-]+(?:\s*,\s*(?:===|==|!=|~=|<=|>=|<|>)'
                    r'\s*[A-Za-z0-9.*+!_-]+)*)?$')


def bilingual(v):
    return isinstance(v, str) or (isinstance(v, dict) and isinstance(v.get('zh'), str) and isinstance(v.get('en'), str))


def check(e):
    problems = []
    if not isinstance(e.get('id'), str) or not ID_RE.match(e['id']):
        problems.append('id')
    for key in ('version', 'url', 'sha256'):
        if not isinstance(e.get(key), str) or not e[key]:
            problems.append(key)
    if not isinstance(e.get('api'), int):
        problems.append('api')
    if not isinstance(e.get('size'), int) or e['size'] <= 0:
        problems.append('size')
    if not re.match(r'^[0-9a-f]{64}$', str(e.get('sha256', ''))):
        problems.append('sha256')
    if not str(e.get('url', '')).startswith('https://'):
        problems.append('url (https only in the public index)')
    if not bilingual(e.get('name')) or not bilingual(e.get('description', '')):
        problems.append('name/description')
    if not all(isinstance(r, str) and REQ_RE.match(r) for r in e.get('requirements', [])):
        problems.append('requirements')
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('entries', nargs='+')
    ap.add_argument('--check-url', action='store_true')
    args = ap.parse_args()
    with open(INDEX, encoding='utf-8') as f:
        index = json.load(f)
    for path in args.entries:
        with open(path, encoding='utf-8') as f:
            e = json.load(f)
        problems = check(e)
        if problems:
            sys.exit(f'{path}: bad {", ".join(problems)}')
        if args.check_url:
            with urllib.request.urlopen(urllib.request.Request(e['url'], headers={'User-Agent': 'add_entry'}),
                                        timeout=120) as r:
                data = r.read()
            sha = hashlib.sha256(data).hexdigest()
            if len(data) != e['size'] or sha != e['sha256']:
                sys.exit(f'{path}: the zip at the URL has {len(data)} bytes / {sha}, the entry says '
                         f'{e["size"]} / {e["sha256"]}')
        index['plugins'] = [p for p in index['plugins'] if p['id'] != e['id']] + [e]
        print(f'{e["id"]} {e["version"]}')
    index['plugins'].sort(key=lambda p: p['id'])
    index['updated'] = datetime.date.today().isoformat()
    with open(INDEX, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
        f.write('\n')


if __name__ == '__main__':
    main()

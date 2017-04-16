import re
import sys
import json
import os
import os.path
import itertools
from collections import namedtuple

from parse import fetched_rows, parse_cells, parse_routes

def get_changes(edit_path):
    with open(edit_path) as f:
        rex = re.compile('changes: ({.*?})')
        for line in f:
            m = rex.search(line)
            if m is not None:
                return json.loads(m.group(1))


def get_tabs(changes, tab_names):
    todo = set(tab_names)
    tabs = {}
    for c in changes['topsnapshot']:
        try:
            name = c[1][4][1][0][3]
        except Exception as e:
            continue
        if name in todo:
            todo.remove(name)
            tabs[c[1][3]] = name
    assert not todo
    return tabs


def fetches(root):
    for fname in os.listdir(root):
        if not fname.startswith('.'):
            with open(os.path.join(root, fname), 'r') as f:
                next(f)
                obj = json.load(f)
                yield fetched_rows(obj)


def _all_routes(tabs, fetches): # type(fetches) == list
    rs = {}
    for tab_id, name in tabs.items():
        flt = list(filter(lambda x: x.tab_id == tab_id and x.raw_cells is not None, fetches))
        srt = sorted(flt, key=lambda x: x.start)
        cells = itertools.chain.from_iterable(map(lambda x: parse_cells(x.raw_cells), srt))
        rs[name] = list(parse_routes(cells))
    return rs


def all_routes(root, tab_names):
    tabs = get_tabs(get_changes(os.path.join(root, 'edit')), tab_names)
    fs = list(fetches(os.path.join(root, 'fetchrows')))
    return _all_routes(tabs, fs)

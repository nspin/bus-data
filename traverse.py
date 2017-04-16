from collections import deque

STOP = 0
SKIP = 1
CONT = 2

# Convenience

def islist(x):
    return type(x) == list

def isdict(x):
    return type(x) == dict


# For dict keys

class Wrap(object):

    def __init__(self, x):
        self.x = x


def traverse(root_, f):

    root = Wrap(root_)

    visited = {}
    props = {}

    def make_path(node):
        curr = node
        path = []
        while curr is not root:
            yield props[curr].x
            curr = visited[curr]

    q = deque([root])

    while len(q):
        node = q.popleft()
        cont = yield from f(node.x)
        if callable(cont):
            cont = yield from cont(make_path(node))
        if cont == STOP:
            return
        elif cont == CONT:
            if isdict(node.x):
                for k, v_ in node.x.items():
                    v = Wrap(v_)
                    visited[v] = node
                    props[v] = (dict, k)
                    q.append(v)
            elif islist(node.x):
                for i, v_ in enumerate(node.x):
                    v = Wrap(v_)
                    visited[v] = node
                    props[v] = (list, i)
                    q.append(v)
        elif cont == SKIP:
            pass
        else:
            raise Exception('[TRAVERSAL ERROR] continuation returned: ' + str(cont))


def format_path(path):
    fmtd = ''
    for kind, k in path:
        fmtd = ('[{}]'.format(k) if kind is list else '.{}'.format(k)) + fmtd
    return fmtd


# f-util

def summary(node):
    if isdict(node):
        return 'dict[{}]'.format(', '.join(node.keys()))
    elif islist(node):
        return 'list[{}]'.format(len(node))
    else:
        return str(node)

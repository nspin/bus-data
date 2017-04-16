import os
import os.path
import time
from mitmproxy import ctx

def ts():
    return int(time.time() * 1000)

root = 'data-{}'.format(ts())

def response(flow):
    if flow.request.path_components[-1] == 'edit':
        with open(os.path.join(root, 'edit'), 'w') as f:
            f.write(flow.response.text)
    elif flow.request.path_components[-1] == 'fetchrows':
        with open(os.path.join(root, 'fetchrows', str(ts())), 'w') as f:
            f.write(flow.response.text)

def start():
    os.makedirs(os.path.join(root, 'fetchrows'))

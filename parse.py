import re
import sys
import json
import itertools
from collections import namedtuple


__all__ = [
    'fetched_rows',
    'parse_cells',
    'parse_routes',
    ]

FetchedRows = namedtuple('FetchedRows', ['tab_id', 'start', 'end', 'raw_cells'])

###
def fetched_rows(obj):
    gr = obj['perGridRangeSnapshots'][0]['gridRange']
    tab_id = gr[1]
    start = gr[2]
    end = gr[3]
    cells = obj['perGridRangeSnapshots'][0]['snapshot'][0][1][4]
    if type(cells) == list and len(cells) == 2 and cells[0] is None and len(cells[1]) == 1:
        snd = cells[1][0]
        if snd[0] == None and snd[1] == 0 and snd[2] == 0 and type(snd[3]) == int:
            cells = None
    return FetchedRows(tab_id, start, end, cells)


REF = 0
NORM = 1
LINK = 2
BREAK = 3

# raw cell -> full cell. YUCK
def parse_cell(cell_):
    if len(cell_) == 26 and type(cell_[-1]) == int and all(x is None for x in itertools.islice(cell_, 25)):
        return (REF, cell_[-1])
    if len(cell_) == 7:
        if all(cell_[i] is None for i in [0, 1, 4, 5]) and cell_[2] == 3 and type(cell_[6]) == int:
            if cell_[3][0] == None and cell_[3][1] == 2:
                if len(cell_[3]) == 3:
                    return (NORM, cell_[6], cell_[3][2], False)
                if len(cell_[3]) == 7 and all(cell_[3][i] is None for i in [3, 4, 5]) and cell_[3][-1] == 1:
                    return (NORM, cell_[6], cell_[3][2], True)
    if len(cell_) == 25:
        ixs = [0,1,3,5,8,10,11,12,13,14,15,16,17,18,19,20,21,22]
        if all(cell_[i] is None for i in ixs) and cell_[2] == 131222 and cell_[9] == 0:
            return (LINK, cell_[4], cell_[6], cell_[7][2], cell_[24])
    if cell_ == [None, None, 1, [None, 2, '']]:
        return (BREAK,)
    raise Exception('parse_cell')


def format_cell(cell): # full cell -> str
    if cell[0] == REF:
        return '={}='.format(cell[1])
    elif cell[0] == NORM:
        return '({}) {} {}'.format(cell[1], cell[2], cell[3])
    elif cell[0] == LINK:
        return '$$ {} {} <{}> {}'.format(cell[1], cell[2], cell[3], cell[4])
    elif cell[0] == BREAK:
        return '-'


def inflate(raw_cells): # raw cells -> inflated full cells
    out = list(map(parse_cell, filter(None, raw_cells)))
    for i in range(len(out)):
        if out[i][0] == REF:
            out[i] = out[out[i][-1]]
    return out


def strip_cell(cell): # full cell -> min cell
    if cell[0] == NORM:
        return (NORM, cell[2])
    elif cell[0] == LINK:
        return (LINK, cell[3], cell[4])


def strip_cells(cells): # full cells -> min cells no break
    return map(strip_cell, filter(lambda x: x[0] != BREAK, cells))


###
def parse_cells(raw_cells): # raw cells -> min cells no break
    return strip_cells(inflate(raw_cells))


Route = namedtuple('Route', ['am_pm', 'name', 'stops', 'buses'])
Stop = namedtuple('Stop', ['name', 'lat', 'lon'])
Bus = namedtuple('Bus', ['name', 'headsign', 'times', 'duration', 'stddev'])

###
def parse_routes(cells): # min cells -> routes

    stop_re = re.compile('https://www.google.com/maps/place/(-?[0-9.]+),(-?[0-9.]+)')

    _, tod = next(cells)
    assert tod == 'AM' or tod == 'PM'

    done = False
    while not done:

        am_pm = tod
        _, route_name = next(cells)

        next(cells)
        next(cells)

        stops = []
        while True:
            cell = next(cells)
            if cell[0] != LINK:
                break
            m = stop_re.match(cell[2])
            stops.append(Stop(cell[1], m.group(1), m.group(2)))

        next(cells)

        buses = []
        while True:
            try:
                _, bus_name = next(cells)
            except StopIteration:
                done = True
                break
            if bus_name == 'AM' or bus_name == 'PM':
                tod = bus_name
                break
            _, headsign = next(cells)
            times = []
            for _ in range(len(stops)):
                times.append(next(cells)[1])
            _, duration = next(cells)
            _, stddev = next(cells)
            buses.append(Bus(bus_name, headsign, times, duration, stddev))

        yield Route(am_pm, route_name, stops, buses)

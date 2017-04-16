import itertools
from xml.sax.saxutils import escape

def indent(n, it):
    for x in it:
        yield ' '*n + x


def mk_doc(name, desc, folders):
    yield '<?xml version="1.0" encoding="UTF-8"?>'
    yield '<kml xmlns="http://www.opengis.net/kml/2.2">'
    yield '  <Document>'
    yield '    <name>' + escape(name) + '</name>'
    yield '    <description>' + escape(desc) + '</description>'
    for f in folders:
        yield from indent(4, f)
    yield '  </Document>'
    yield '</kml>'


def mk_folder(name, desc, it):
    yield '<Folder>'
    yield '  <name>' + escape(name) + '</name>'
    yield '  <description>' + escape(desc) + '</description>'
    for x in it:
        yield from indent(2, x)
    yield '</Folder>'


def mk_pm(name, desc, lat, lon):
    yield '<Placemark>'
    yield '  <name>' + escape(name) + '</name>'
    yield '  <description>' + escape(desc) + '</description>'
    yield '  <Point>'
    yield '    <coordinates>' + escape(lon) + ',' + escape(lat) + '</coordinates>'
    yield '  </Point>'
    yield '</Placemark>'


def folders(all_rs):
    for name, routes in all_rs.items():
        am_, pm_ = itertools.tee(routes)
        am = mk_folder('AM', '', pms(filter(lambda x: x.am_pm == 'AM', am_)))
        pm = mk_folder('PM', '', pms(filter(lambda x: x.am_pm == 'PM', pm_)))
        yield mk_folder(name, '', [am, pm])


def pms(routes):
    for am_pm, name, stops, buses in routes:
        for i, stop in enumerate(stops):
            desc = '\n'.join([
                am_pm,
                name,
                ', '.join(map(lambda x: x.times[i], buses))
                ])
            yield mk_pm(stop.name, desc, stop.lat, stop.lon)


def dump(routes, f):
    for line in mk_doc('[redacted] Map', '', folders(routes)):
        f.write(line)
        f.write('\n')

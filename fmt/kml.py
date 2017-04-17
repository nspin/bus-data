import sys
import random
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
    yield from indent(4, folders)
    yield '  </Document>'
    yield '</kml>'

def mk_folder(name, desc, it):
    yield '<Folder>'
    yield '  <name>' + escape(name) + '</name>'
    yield '  <description>' + escape(desc) + '</description>'
    yield from indent(2, it)
    yield '</Folder>'

def mk_pm(style_id, name, desc, mark):
    yield '<Placemark>'
    yield '  <styleUrl>#' + style_id + '</styleUrl>'
    yield '  <name>' + escape(name) + '</name>'
    yield '  <description>' + escape(desc) + '</description>'
    yield from indent(2, mark)
    yield '</Placemark>'

def mk_pt(lat, lon):
    yield '<Point>'
    yield '  <coordinates>' + escape(lon) + ',' + escape(lat) + '</coordinates>'
    yield '</Point>'

def mk_line(coords):
    yield '<LineString>'
    yield '  <extrude>1</extrude>'
    yield '  <tessellate>1</tessellate>'
    yield '  <coordinates>' + '\n'.join(map(lambda x: escape(x[1]) + ',' + escape(x[0]), coords)) + '</coordinates>'
    yield '</LineString>'


class KML(object):

    def __init__(self):
        self.colors = []


    def to_id(self, color):
        return 'line-{}'.format(color)


    def all_styles(self):
        for color in self.colors:
            style_id = self.to_id(color)
            yield '<Style id="' + escape(style_id) + '">'
            yield '  <IconStyle>'
            yield '    <color>' + escape(color) + '</color>'
            yield '    <scale>1</scale>'
            yield '    <Icon>'
            yield '      <href>http://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>'
            yield '    </Icon>'
            yield '  </IconStyle>'
            yield '  <LabelStyle>'
            yield '    <scale>0</scale>'
            yield '  </LabelStyle>'
            yield '  <LineStyle>'
            yield '    <color>' + escape(color) + '</color>'
            yield '    <width>1</width>'
            yield '  </LineStyle>'
            yield '</Style>'


    def get_style(self):
        color = ''.join(random.choice(list('0123456789abc')) for _ in range(8))
        self.colors.append(color)
        return self.to_id(color)


    def folders(self, all_rs):
        for name, routes in all_rs.items():
            am_, pm_ = itertools.tee(routes)
            yield from mk_folder('[AM] ' + name, '', self.pms(filter(lambda x: x.am_pm == 'AM', am_)))
            yield from mk_folder('[PM] ' + name, '', self.pms(filter(lambda x: x.am_pm == 'PM', pm_)))


    def pms(self, routes):
        for am_pm, name, stops, buses in routes:
            style_id = self.get_style()
            full_name = '[{}] {}'.format(am_pm, name)
            desc = 'Stops:' + ''.join(map(lambda x: '\n  - {}'.format(x.name), stops))
            yield from mk_pm(style_id, full_name, desc, mk_line(map(lambda x: (x.lat, x.lon), stops)))
            for i, stop in enumerate(stops):
                sdesc = '\n'.join(itertools.chain([
                        'Bus: ' + full_name,
                        'Stop: ' + stop.name,
                        'Times:',
                    ], map(lambda x: '  - {}'.format(x.times[i]), buses)
                    ))
                yield from mk_pm(style_id, stop.name, sdesc, mk_pt(stop.lat, stop.lon))


def dump(routes, f):
    k = KML()
    for line in mk_doc('[redacted] Map', '', itertools.chain(k.folders(routes), k.all_styles())):
        f.write(line)
        f.write('\n')

def rows(routes):
    for tab, rts in routes.items():
        for am_pm, rt_name, stops, buses in rts:
            for i, stop in enumerate(stops):
                name = '[{}: {}] {}'.format(rt_name, am_pm, stop.name)
                desc = ', '.join(map(lambda x: x.times[i], buses))
                yield name, stop.lat, stop.lon, desc

def dump(routes, f):
    f.write('\t'.join(['Name', 'Latitude', 'Longitude', 'Description']))
    f.write('\n')
    for row in rows(routes):
        f.write('\t'.join(row))
        f.write('\n')

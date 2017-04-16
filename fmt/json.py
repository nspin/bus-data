import json

def fancy_route(rt):
    return {
        'am_pm': rt.am_pm,
        'name': rt.name,
        'stops': list(map(lambda x: x._asdict(), rt.stops,)),
        'buses': list(map(lambda x: x._asdict(), rt.buses)),
        }

def fancy(routes):
    return {
        tab_name: list(map(fancy_route, rts))
        for tab_name, rts in routes.items()
        }

def dump(routes, f):
    return json.dump(fancy(routes), f)

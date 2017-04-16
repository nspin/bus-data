import fmt.json
import fmt.kml
import fmt.tsv

def dump(fmt_name, routes, f):
    return getattr(fmt, fmt_name).dump(routes, f)

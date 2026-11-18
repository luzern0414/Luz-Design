"""One package dispatch boundary; a receipt never relaxes another UI mode."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys


def mode(package):
    package = Path(package).resolve()
    found = [name for name in ('luz-component-ui.json','luz-frontend.json') if (package/name).is_file()]
    if len(found) != 1:
        raise ValueError('UI package requires exactly one recognized mode receipt')
    return {'luz-component-ui.json':'component-reuse','luz-frontend.json':'frontend'}[found[0]]


def verify_package(package, *, session, require_audit=True):
    selected = mode(package)
    if selected == 'frontend':
        from frontend import verify_package as verify
        result = verify(package,session,require_audit=require_audit)
    else:
        from component_ui import verify_package as verify
        result = verify(package,session,require_audit=require_audit)
    return {**result,'mode':selected}


def export_package(package, *, session, out):
    selected = mode(package)
    if selected == 'frontend':
        from frontend import export
        return export(package,session,out)
    from component_ui import export
    return export(package,session,out)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['check','export'])
    parser.add_argument('package');parser.add_argument('--session',required=True);parser.add_argument('--out')
    args=parser.parse_args()
    try:
        if args.action=='export':
            if not args.out: raise ValueError('export requires --out')
            result=export_package(args.package,session=args.session,out=args.out)
        else: result=verify_package(args.package,session=args.session)
        print(json.dumps(result,ensure_ascii=False,indent=2,default=str));return 0
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())

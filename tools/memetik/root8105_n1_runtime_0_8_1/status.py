"""Small read-only status; does not start a session or alter run accounts."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import guard
import runtime as r

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    root = parser.parse_args().root.resolve()
    s = r.read(root/'state.json')
    child = s.get('child')
    live = guard.stat(child) if child else None
    result = dict(time=datetime.now().astimezone().isoformat(timespec='seconds'),
                  status=s['status'], phase=s.get('phase'), child=child, live_process=live,
                  memory_pressure=s.get('memory_pressure'), native_request=s.get('request'),
                  aggregate_request=(s.get('guard') or {}).get('request'),
                  stop_reason=(s.get('guard') or {}).get('stop_reason'))
    print(json.dumps(result, indent=2))

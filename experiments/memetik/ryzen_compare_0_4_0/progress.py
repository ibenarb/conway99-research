"""Single-writer console rendering; all verified worker records remain on disk."""
import json
import time

TARGETS = ("W", "L1", "F", "Linf")


def render(event):
    from search import key
    indent = " " * (25 * TARGETS.index(event["target"]))
    stamp = time.strftime("%H:%M:%S", time.localtime(event["wall"]))
    value = key(event["scores"], event["target"])
    label = "(W,L1)" if event["target"] == "W" else event["target"]
    return (f"{indent}{stamp} {event['arm']}/{event['variant']}/r{event['replicate']+1:02d} "
            f"{label}={value} CPU={event['cpu']:.1f}s "
            f"Abstand={event['gap_wall_seconds']:.1f}s")


class Progress:
    def __init__(self, directory, quiet_seconds=300):
        self.directory = directory
        self.quiet_seconds = quiet_seconds
        self.started = time.monotonic()
        self.last_poll = float('-inf')
        # Old records stay in files but are not printed again after resume.
        self.offsets = {p: p.stat().st_size for p in directory.glob('tasks/*/improvements.jsonl')}

    def poll(self, force=False):
        now = time.monotonic()
        if not force and now-self.last_poll < 2:
            return
        self.last_poll = now
        for path in sorted(self.directory.glob('tasks/*/improvements.jsonl')):
            with path.open('rb') as stream:
                stream.seek(self.offsets.get(path, 0))
                while True:
                    offset = stream.tell()
                    line = stream.readline()
                    if not line.endswith(b'\n'):
                        self.offsets[path] = offset
                        break
                    event = json.loads(line)
                    if now-self.started >= self.quiet_seconds:
                        print(render(event), flush=True)
                    self.offsets[path] = stream.tell()

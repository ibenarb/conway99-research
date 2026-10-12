"""Incremental binary DRAT/LRAT counters. Telemetry never validates a proof."""
from pathlib import Path


class ProofCounter:
    def __init__(self, path, mode):
        self.path = Path(path)
        self.mode = mode
        self.offset = 0
        self.zeros_needed = 0
        self.kind = None
        self.additions = 0
        self.deletions = 0
        self.error = None

    def sample(self, maximum=4 * 1024 ** 2):
        if self.error or not self.path.exists():
            return self.result()
        try:
            with self.path.open('rb') as stream:
                stream.seek(self.offset)
                chunk = stream.read(maximum)
            for byte in chunk:
                if not self.zeros_needed:
                    if byte not in (ord('a'), ord('d')):
                        raise ValueError('Unexpected binary proof opcode; counters disabled')
                    self.kind = chr(byte)
                    self.zeros_needed = 2 if self.mode == 'lrat' and self.kind == 'a' else 1
                elif byte == 0:
                    self.zeros_needed -= 1
                    if not self.zeros_needed:
                        if self.kind == 'a':
                            self.additions += 1
                        else:
                            self.deletions += 1
            self.offset += len(chunk)
        except (OSError, ValueError) as error:
            self.error = str(error)
        return self.result()

    def result(self):
        size = self.path.stat().st_size if self.path.exists() else 0
        return {'scanned_bytes': self.offset, 'file_bytes': size,
                'scan_backlog_bytes': max(0, size - self.offset),
                'complete_addition_records_in_scanned_prefix': self.additions,
                'complete_deletion_records_in_scanned_prefix': self.deletions,
                'error': self.error, 'scope': 'Telemetry only; counts may lag; no ETA or validation claim'}

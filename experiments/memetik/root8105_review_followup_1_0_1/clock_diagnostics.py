import bootstrap
"""Explicit, comparable clock anchors; drift is diagnosed, never rescaled."""
import time


class ClockDiagnostics:
    def __init__(self, monotonic_start, utc_start, host_required):
        self.start = {'guest_monotonic_s': monotonic_start, 'guest_utc_s': utc_start}
        self.host_required = host_required
        self.anchor = None

    def observe(self, monotonic, utc, host=None, error=None):
        result = {'session_anchor': self.start, 'host_anchor': self.anchor,
                  'guest_monotonic_s': monotonic, 'guest_utc_s': utc,
                  'source': 'Windows Stopwatch vs WSL monotonic' if self.host_required
                            else 'Linux monotonic vs UTC', 'ok': False, 'error': error}
        guest_elapsed = monotonic - self.start['guest_monotonic_s']
        utc_elapsed = utc - self.start['guest_utc_s']
        result.update(guest_elapsed_s=guest_elapsed, guest_utc_elapsed_s=utc_elapsed,
                      guest_utc_deviation_s=guest_elapsed - utc_elapsed)
        if not self.host_required:
            result['tolerance_s'] = max(2, abs(utc_elapsed) * .01)
            result['ok'] = abs(guest_elapsed - utc_elapsed) <= result['tolerance_s']
            result['reason'] = 'OK_NATIVE' if result['ok'] else 'GUEST_MONOTONIC_UTC_MISMATCH'
            return result
        if host is None:
            result['reason'] = 'HOST_READ_ERROR' if error else 'HOST_NOT_YET_AVAILABLE'
            return result
        freshness = utc - host['utc_s']
        result['host_sample'] = host
        result['freshness_s'] = freshness
        if abs(freshness) >= 15:
            result['reason'] = 'HOST_STALE_OR_UTC_MISMATCH'
            return result
        if self.anchor is None:
            self.anchor = {'host_stopwatch_s': host['stopwatch_s'], 'host_utc_s': host['utc_s'],
                           'guest_monotonic_s': monotonic, 'guest_utc_s': utc,
                           'host_pid': host.get('pid')}
        result['host_anchor'] = self.anchor
        hd = host['stopwatch_s'] - self.anchor['host_stopwatch_s']
        gd = monotonic - self.anchor['guest_monotonic_s']
        hu = host['utc_s'] - self.anchor['host_utc_s']
        tolerance = max(5, abs(hd) * .02)
        result.update(host_stopwatch_delta_s=hd, guest_monotonic_delta_s=gd,
                      host_utc_delta_s=hu, deviation_s=gd - hd, tolerance_s=tolerance,
                      host_internal_deviation_s=hu - hd)
        if host.get('pid') != self.anchor['host_pid'] or hd < 0:
            result['reason'] = 'HOST_IDENTITY_OR_CLOCK_RESET'
        elif hd < 30:
            result['reason'] = 'ANCHOR_WARMUP'
        elif abs(gd - hd) > tolerance:
            result['reason'] = 'HOST_WSL_DELTA_MISMATCH'
        elif abs(hu - hd) > max(2, abs(hd) * .01):
            result['reason'] = 'HOST_UTC_STOPWATCH_MISMATCH'
        else:
            result['ok'], result['reason'] = True, 'OK_HOST_COMPARISON'
        return result

"""Only change to P: enable the complete cycle3 catalogue."""
import boot
from engine import Engine as FrozenEngine

class PCEngine(FrozenEngine):
    def batch(self, current, guard, sample_size=None):
        original = self.variant
        if original == "PC":
            self.variant = "TC"
        try:
            return super().batch(current, guard, sample_size)
        finally:
            self.variant = original

    def step(self, guard):
        if self.variant == "PC":
            self.step_episode(guard)
        else:
            super().step(guard)

    def finish_episode(self, reason):
        if self.variant == "PC" and reason == "LOCAL_MIN_EXACT_AP":
            reason = "LOCAL_MIN_EXACT_APC"
        super().finish_episode(reason)

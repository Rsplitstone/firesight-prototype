from datetime import datetime
from itertools import chain


def fuse_streams(*streams):
    """Merge and sort entries from multiple streams by timestamp."""
    fused = list(chain(*streams))
    fused.sort(key=lambda x: x["timestamp"])
    return fused

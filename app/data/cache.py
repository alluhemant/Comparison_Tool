from functools import lru_cache
from app.models import ComparisonResult


class ComparisonCache:
    def __init__(self, max_size=100):
        self.cache = lru_cache(maxsize=max_size)

    def get(self, comparison_id: int) -> ComparisonResult:
        return self.cache.get(comparison_id)

    def set(self, result: ComparisonResult):
        self.cache[result.id] = result
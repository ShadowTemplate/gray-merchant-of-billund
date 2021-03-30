from pathlib import Path
from typing import Dict, Generator, Sequence

from gray_merchant_of_billund.constants.gmob import IMMUTABLE_STORAGE_DIR
from gray_merchant_of_billund.model.base_set import BaseIndex, BaseSet


class RebrickableSet(BaseSet):
    def __init__(
        self,
        base_lego_set: BaseSet,
        theme_id: str,
        num_parts: int,
    ):
        super().__init__(
            base_lego_set.num,
            base_lego_set.name,
            base_lego_set.year,
        )
        self.theme_id: str = theme_id
        self.num_parts: int = num_parts

    def __str__(self):
        return f"{super().__str__()} |{self.num_parts}|"

    @property
    def store_key(self) -> str:
        return self.num

    @staticmethod
    def store_dir() -> str:
        return (Path(IMMUTABLE_STORAGE_DIR) / "RebrickableSet").as_posix()


class RebrickableIndex(BaseIndex):
    def __init__(self, sets: Sequence[RebrickableSet]):
        super().__init__(sets)
        self.sets: Sequence[RebrickableSet] = sets
        self._index: Dict[str, int] = {
            lego_set.num: index for index, lego_set in enumerate(self.sets)
        }

    def __iter__(self) -> Generator[RebrickableSet, None, None]:
        index: int = 0
        while index < self.size:
            yield self.sets[index]
            index += 1

    @property
    def tot_num_parts(self) -> int:
        return sum(s.num_parts for s in self.sets)

    @property
    def avg_num_parts(self) -> float:
        return self.tot_num_parts / self.size

    @property
    def median_num_parts(self) -> float:
        sorted_sets = self.top_n_large(self.size)
        if self.size % 2 == 1:
            return sorted_sets[self.size // 2].num_parts
        return (
            sorted_sets[self.size // 2].num_parts
            + sorted_sets[self.size // 2 - 1].num_parts
        ) / 2

    def larger_than(self, threshold: int) -> Sequence[RebrickableSet]:
        return list(filter(lambda s: s.num_parts > threshold, self.sets))

    def top_n_large(self, n: int) -> Sequence[RebrickableSet]:
        return sorted(self.sets, key=lambda s: -s.num_parts)[:n]

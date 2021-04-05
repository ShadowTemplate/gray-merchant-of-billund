from pathlib import Path
from typing import Dict, Generator, List, Sequence, Tuple

from gray_merchant_of_billund.constants.gmob import MUTABLE_STORAGE_DIR
from gray_merchant_of_billund.model.bricklink_price import PriceGuide
from gray_merchant_of_billund.model.rebrickable_set import (
    RebrickableIndex,
    RebrickableSet,
)
from gray_merchant_of_billund.storage.expirable import Expirable
from gray_merchant_of_billund.utils.time import now


class BricklinkSet(RebrickableSet, Expirable):
    def __init__(
        self,
        rebrickable_lego_set: RebrickableSet,
        for_sale: int,
        on_wanted: int,
        price_guide: PriceGuide,
    ):
        super().__init__(
            rebrickable_lego_set,
            rebrickable_lego_set.theme_id,
            rebrickable_lego_set.num_parts,
        )
        self.for_sale: int = for_sale
        self.on_wanted: int = on_wanted
        self.price_guide: PriceGuide = price_guide
        self._now: int = now()

    def __str__(self):
        return (
            f"{super().__str__()} "
            f"Sale: {self.for_sale}, "
            f"Wanted: {self.on_wanted}"
        )

    @staticmethod
    def store_dir() -> str:
        return (Path(MUTABLE_STORAGE_DIR) / "BricklinkSet").as_posix()

    @property
    def creation_date_ms(self) -> int:
        return self._now


class BricklinkIndex(RebrickableIndex):
    def __init__(self, sets: Sequence[BricklinkSet]):
        super().__init__(sets)
        self.sets: Sequence[BricklinkSet] = sets
        self._index: Dict[str, int] = {
            lego_set.num: index for index, lego_set in enumerate(self.sets)
        }

    def __iter__(self) -> Generator[BricklinkSet, None, None]:
        index: int = 0
        while index < self.size:
            yield self.sets[index]
            index += 1

    def top_n_rare(self, n: int) -> Sequence[BricklinkSet]:
        return sorted(self.sets, key=lambda s: s.for_sale)[:n]

    def top_n_wanted(self, n: int) -> Sequence[BricklinkSet]:
        return sorted(self.sets, key=lambda s: -s.on_wanted)[:n]

    @property
    def total_current_used_avg_price(
        self,
    ) -> Tuple[float, Sequence[BricklinkSet]]:
        total_current_used: float = 0
        missing: List[BricklinkSet] = []
        for lego_set in self:
            if lego_set.price_guide.aggregate_current_used:
                total_current_used += (
                    lego_set.price_guide.aggregate_current_used.avg_price
                )
            else:
                missing.append(lego_set)
        return total_current_used, missing

    @property
    def total_current_new_avg_price(
        self,
    ) -> Tuple[float, Sequence[BricklinkSet]]:
        total_current_new: float = 0
        missing: List[BricklinkSet] = []
        for lego_set in self:
            if lego_set.price_guide.aggregate_current_new:
                total_current_new += (
                    lego_set.price_guide.aggregate_current_new.avg_price
                )
            else:
                missing.append(lego_set)
        return total_current_new, missing

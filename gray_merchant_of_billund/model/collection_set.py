from pathlib import Path
from typing import Dict, Generator, Optional, Sequence

from gray_merchant_of_billund.constants.gmob import IMMUTABLE_STORAGE_DIR
from gray_merchant_of_billund.model.base_set import BaseIndex, BaseSet


class CollectionSet(BaseSet):
    def __init__(
        self,
        base_lego_set: BaseSet,
        purchase_price: Optional[float],
        price_notes: Optional[str],
        acquired_date: Optional[str],
        date_notes: Optional[str],
        gift: bool,
        instructions: bool,
        acquired_location: Optional[str],
        acquired_new: bool,
        other_notes: Optional[str],
    ):
        super().__init__(
            base_lego_set.num,
            base_lego_set.name,
            base_lego_set.year,
        )
        self.purchase_price: Optional[float] = purchase_price
        self.price_notes: Optional[str] = price_notes
        self.acquired_date: Optional[str] = acquired_date
        self.date_notes: Optional[str] = date_notes
        self.gift: bool = gift
        self.instructions: bool = instructions
        self.acquired_location: Optional[str] = acquired_location
        self.acquired_new: bool = acquired_new
        self.other_notes: Optional[str] = other_notes

    def __str__(self):
        return (
            f"{super().__str__()} "
            f"{'💖' if self.acquired_new else '💞'}"
            f"{'🎁' if self.gift else ''}"
            f"{'📖' if self.instructions else ''} "
            f"({self.purchase_price} €"
            f"{'. ' + self.price_notes if self.price_notes else ''}) "
            f"({self.acquired_date}"
            f"{'. ' + self.date_notes if self.date_notes else ''})"
        )

    @staticmethod
    def store_dir() -> str:
        return (Path(IMMUTABLE_STORAGE_DIR) / "CollectionSet").as_posix()


class CollectionIndex(BaseIndex):
    def __init__(self, sets: Sequence[CollectionSet]):
        super().__init__(sets)
        self.sets: Sequence[CollectionSet] = sets
        self._index: Dict[str, int] = {
            lego_set.num: index for index, lego_set in enumerate(self.sets)
        }

    def __iter__(self) -> Generator[CollectionSet, None, None]:
        index: int = 0
        while index < self.size:
            yield self.sets[index]
            index += 1

    @property
    def tot_purchase_price(self) -> float:
        return sum(s.purchase_price for s in self.sets if s.purchase_price)

    @property
    def actually_paid_price(self) -> float:
        return sum(
            s.purchase_price
            for s in self.sets
            if s.purchase_price and not s.gift
        )

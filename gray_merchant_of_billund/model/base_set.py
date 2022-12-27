from pathlib import Path
from typing import Dict, Generator, Sequence, Sized

from gray_merchant_of_billund.constants.gmob import (
    BRICKLINK_SET_HISTORY_COMPLETE_URL,
    BRICKLINK_SET_SHOP_URL,
    BRICKSET_SET_URL,
    IMMUTABLE_STORAGE_DIR,
    LEGO_SET_SHOP_URL,
)
from gray_merchant_of_billund.storage.saveable import Saveable


class BaseSet(Saveable):
    def __init__(self, num: str, name: str, year: str):
        self.num: str = num
        self.name: str = name
        self.year: str = year

    def __str__(self):
        return f"{self.num}: {self.name} ({self.year})"

    @property
    def link_lego(self) -> str:
        return f"{LEGO_SET_SHOP_URL.format(num=self.num.split('-')[0])}"

    @property
    def link_bricklink(self) -> str:
        return f"{BRICKLINK_SET_SHOP_URL.format(num=self.num)}"

    @property
    def link_bricklink_set_history(self) -> str:
        return f"{BRICKLINK_SET_HISTORY_COMPLETE_URL.format(num=self.num)}"

    @property
    def link_bricklink_box_history(self) -> str:
        return f"{BRICKLINK_SET_HISTORY_COMPLETE_URL.format(num=self.num)}"

    @property
    def link_brickset(self) -> str:
        return f"{BRICKSET_SET_URL.format(num=self.num)}"

    @property
    def store_key(self) -> str:
        return self.num

    @staticmethod
    def store_dir() -> str:
        return (Path(IMMUTABLE_STORAGE_DIR) / "BaseSet").as_posix()


class BaseIndex(Sized):
    def __init__(self, sets: Sequence[BaseSet]):
        self.sets: Sequence[BaseSet] = sets
        self.size: int = len(sets)
        self._index: Dict[str, int] = {
            lego_set.num: index for index, lego_set in enumerate(self.sets)
        }

    def __iter__(self) -> Generator[BaseSet, None, None]:
        index: int = 0
        while index < self.size:
            yield self.sets[index]
            index += 1

    def __str__(self):
        return "\n".join(str(lego_set) for lego_set in self.sets)

    def __getitem__(self, set_num):
        return self.sets[self._index[set_num]]

    def __len__(self) -> int:
        return self.size

    def __contains__(self, set_num):
        return set_num in self._index

    def save(self):
        for lego_set in self.sets:
            lego_set.save()

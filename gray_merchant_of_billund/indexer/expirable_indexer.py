from abc import ABCMeta, abstractmethod
from typing import List, Optional, Sequence

from gray_merchant_of_billund.indexer.bricklink_indexer import (
    _get_bricklink_set,
)
from gray_merchant_of_billund.indexer.brickset_indexer import _get_brickset_set
from gray_merchant_of_billund.model.bricklink_set import (
    BricklinkIndex,
    BricklinkSet,
)
from gray_merchant_of_billund.model.brickset_set import (
    BricksetIndex,
    BricksetSet,
)
from gray_merchant_of_billund.model.collection_set import CollectionIndex
from gray_merchant_of_billund.model.rebrickable_set import (
    RebrickableIndex,
    RebrickableSet,
)
from gray_merchant_of_billund.storage.expirable import load
from gray_merchant_of_billund.utils.utils_resources import (
    get_personal_collection,
    get_personal_index,
    get_rebrickable_index,
)


class ExpirableIndexer(metaclass=ABCMeta):
    def __init__(self, time_to_live_ms: Optional[int] = None):
        self.time_to_live_ms: Optional[int] = time_to_live_ms

    def _fetch_items(self, index: RebrickableIndex) -> Sequence[BricksetSet]:
        index_items: List[BricksetSet] = []
        for lego_set in index:
            expirable_item: Optional[BricksetSet] = self.load_from_storage(
                lego_set
            )
            if not expirable_item:
                expirable_item = self.build_from_rebrickable(lego_set)
                expirable_item.save()
            index_items.append(expirable_item)
        return index_items

    @abstractmethod
    def load_from_storage(
        self,
        rebrickable_set: RebrickableSet,
    ) -> Optional[BricksetSet]:
        pass

    @abstractmethod
    def build_from_rebrickable(
        self,
        rebrickable_set: RebrickableSet,
    ) -> BricksetSet:
        pass


class BricksetIndexer(ExpirableIndexer):
    def __init__(
        self, index: RebrickableIndex, time_to_live_ms: Optional[int] = None
    ):
        super().__init__(time_to_live_ms)
        self.items: Sequence[BricksetSet] = self._fetch_items(index)

    def load_from_storage(
        self, rebrickable_set: RebrickableSet
    ) -> Optional[BricksetSet]:
        return load(
            BricksetSet, rebrickable_set.store_key, self.time_to_live_ms
        )

    def build_from_rebrickable(
        self, rebrickable_set: RebrickableSet
    ) -> BricksetSet:
        return _get_brickset_set(rebrickable_set)

    def build(self) -> BricksetIndex:
        return BricksetIndex(self.items)


class BricklinkIndexer(ExpirableIndexer):
    def __init__(
        self, index: RebrickableIndex, time_to_live_ms: Optional[int] = None
    ):
        super().__init__(time_to_live_ms)
        self.items: Sequence[BricklinkSet] = self._fetch_items(index)

    def load_from_storage(
        self, rebrickable_set: RebrickableSet
    ) -> Optional[BricklinkSet]:
        return load(
            BricklinkSet, rebrickable_set.store_key, self.time_to_live_ms
        )

    def build_from_rebrickable(
        self, rebrickable_set: RebrickableSet
    ) -> BricklinkSet:
        return _get_bricklink_set(rebrickable_set)

    def build(self) -> BricklinkIndex:
        return BricklinkIndex(self.items)


def main():
    rebrickable_index: RebrickableIndex = get_rebrickable_index()
    my_collection: CollectionIndex = get_personal_collection()
    my_index: RebrickableIndex = get_personal_index(
        my_collection,
        rebrickable_index,
    )
    brickset_index: BricksetIndex = BricksetIndexer(my_index).build()
    for brickset_set in brickset_index:
        print(brickset_set)
    bricklink_index: BricklinkIndex = BricklinkIndexer(my_index).build()
    for bricklink_set in bricklink_index:
        print(bricklink_set)


if __name__ == "__main__":
    main()

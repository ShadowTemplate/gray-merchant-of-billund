from gray_merchant_of_billund.indexer.bricklink_indexer import (
    _get_bricklink_set,
)

# from gray_merchant_of_billund.indexer.brickset_indexer import _get_brickset_set
from gray_merchant_of_billund.model.base_set import BaseSet
from gray_merchant_of_billund.model.bricklink_set import BricklinkSet
from gray_merchant_of_billund.model.rebrickable_set import RebrickableIndex

# from gray_merchant_of_billund.storage.saveable import load
from gray_merchant_of_billund.storage.expirable import load
from gray_merchant_of_billund.utils.utils_resources import (
    get_rebrickable_index,
)


def main():
    bs = BaseSet("217-1", "Service Station", "1977")
    print(bs)
    bs.save()
    # bs2: BaseSet = load(BaseSet, '217-1')
    # bs2: BaseSet = load(BaseSet, '218-1')
    # print(bs2)
    rebrickable_index: RebrickableIndex = get_rebrickable_index()
    bnk: BricklinkSet = _get_bricklink_set(rebrickable_index["217-1"])
    bnk.save()
    from gray_merchant_of_billund.utils.time import HOUR, MINUTE, SECOND, YEAR

    bnk: BricklinkSet = load(BricklinkSet, "217-1", SECOND)
    print(bnk)
    print(bnk.on_wanted)

    print(bnk.is_expired(YEAR))
    print(bnk.is_expired(HOUR))
    print(bnk.is_expired(5 * MINUTE))
    print(bnk.is_expired(SECOND))


if __name__ == "__main__":
    main()

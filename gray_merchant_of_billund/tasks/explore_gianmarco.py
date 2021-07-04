from gray_merchant_of_billund.constants.gmob import RESOURCES_DIR
from gray_merchant_of_billund.indexer.bricklink_indexer import (
    get_bricklink_index,
)
from gray_merchant_of_billund.indexer.brickset_indexer import (
    get_brickset_index,
)
from gray_merchant_of_billund.model.bricklink_set import BricklinkIndex
from gray_merchant_of_billund.model.brickset_set import BricksetIndex
from gray_merchant_of_billund.model.collection_set import CollectionIndex
from gray_merchant_of_billund.model.rebrickable_set import RebrickableIndex
from gray_merchant_of_billund.utils.path import posix_path
from gray_merchant_of_billund.utils.utils_resources import (
    get_personal_collection,
    get_personal_index,
    get_rebrickable_index,
)


def explore():
    separator = "-" * 25

    my_wishlist: CollectionIndex = get_personal_collection(
        posix_path(RESOURCES_DIR, "gianmarco.txt")
    )
    print(f"Sets: {len(my_wishlist)}")
    print(separator)
    for lego_set in my_wishlist:
        print(
            f"{lego_set.name}: "
            f"{lego_set.purchase_price} vs {lego_set.other_notes} "
            f"(-{100 - (float(lego_set.other_notes) * 100 / lego_set.purchase_price)}%)"
            f"| 15%: {lego_set.purchase_price - (15 * lego_set.purchase_price / 100)}"
        )
    print(separator)

    rebrickable_index: RebrickableIndex = get_rebrickable_index()
    my_index: RebrickableIndex = get_personal_index(
        my_wishlist,
        rebrickable_index,
    )

    bricklink_index: BricklinkIndex = get_bricklink_index(my_index)
    print(bricklink_index)
    print(separator)
    for lego_set in bricklink_index:
        print(f"{lego_set.num}: {lego_set.name}: {lego_set.link_bricklink}")
    print(separator)

    print("Bricklink current used min/avg price:")
    for lego_set in bricklink_index:
        price_guide = lego_set.price_guide
        if price_guide.details_current_used and price_guide.aggregate_current_used:
            min_price = price_guide.details_current_used.min_price
            avg_price = price_guide.aggregate_current_used.avg_price
            print(
                f"{lego_set.num}: {lego_set.name} ({lego_set.year}): {min_price}/{avg_price} €"
            )
        else:
            print(
                f"{lego_set.num}: {lego_set.name} ({lego_set.year}): nothing on the market right now!"
            )
    print(separator)
    total_min, missing = bricklink_index.total_current_used_min_price
    total_avg, missing = bricklink_index.total_current_used_avg_price
    print(
        f"Bricklink current used total min price: {total_min:.2f} € ({len(missing)} sets missing)"
    )
    print(
        f"Bricklink current used total avg price: {total_avg:.2f} € ({len(missing)} sets missing)"
    )
    if len(missing) > 0:
        print("Missing sets:")
        for lego_set in missing:
            print(f"{lego_set.num}: {lego_set.name} ({lego_set.year})")
    print(separator)

    print("Bricklink current new min/avg price")
    for lego_set in bricklink_index:
        price_guide = lego_set.price_guide
        if price_guide.details_current_new and price_guide.aggregate_current_new:
            min_price = price_guide.details_current_new.min_price
            avg_price = price_guide.aggregate_current_new.avg_price
            print(
                f"{lego_set.num}: {lego_set.name} ({lego_set.year}): {min_price}/{avg_price} €"
            )
        else:
            print(
                f"{lego_set.num}: {lego_set.name} ({lego_set.year}): nothing on the market right now!"
            )
    print(separator)
    total_min, missing = bricklink_index.total_current_new_min_price
    total_avg, missing = bricklink_index.total_current_new_avg_price
    print(
        f"Bricklink current new total min price: {total_min:.2f} € ({len(missing)} sets missing)"
    )
    print(
        f"Bricklink current new total avg price: {total_avg:.2f} € ({len(missing)} sets missing)"
    )
    if len(missing) > 0:
        print("Missing sets:")
        for lego_set in missing:
            print(f"{lego_set.num}: {lego_set.name} ({lego_set.year})")
    print(separator)


if __name__ == "__main__":
    explore()

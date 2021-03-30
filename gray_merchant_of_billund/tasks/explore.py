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
        posix_path(RESOURCES_DIR, "wishlist.txt")
    )
    print(f"Sets: {len(my_wishlist)}")
    print(f"Price: {my_wishlist.tot_purchase_price}")
    print(my_wishlist)
    print(separator)

    rebrickable_index: RebrickableIndex = get_rebrickable_index()
    my_index: RebrickableIndex = get_personal_index(
        my_wishlist,
        rebrickable_index,
    )

    print(f"Indexed sets ({len(my_index)}):")
    print(my_index)
    print(separator)

    print(f"Total parts: {my_index.tot_num_parts}")
    print(f"Avg set parts: {my_index.avg_num_parts}")
    print(f"Median set parts: {my_index.median_num_parts}")
    print(separator)

    big_set_threshold = 999
    print(f"Sets > {big_set_threshold} parts:")
    for top_set in my_index.larger_than(big_set_threshold):
        print(f"{top_set.num}: {top_set.name}: {top_set.num_parts} parts")
    print(separator)

    top_n = len(my_wishlist)
    print(f"Top-{top_n} num parts:")
    for top_set in my_index.top_n_large(top_n):
        print(f"{top_set.num}: {top_set.name}: {top_set.num_parts} parts")
    print(separator)

    bricklink_index: BricklinkIndex = get_bricklink_index(my_index)
    print(bricklink_index)
    print(separator)

    print(f"Top-{top_n} rarest:")
    for top_set in bricklink_index.top_n_rare(top_n):
        print(f"{top_set.num}: {top_set.name}: {top_set.for_sale} for sale")
    print(separator)

    print(f"Top-{top_n} most wanted:")
    for top_set in bricklink_index.top_n_wanted(top_n):
        print(f"{top_set.num}: {top_set.name}: {top_set.on_wanted} wanted")
    print(separator)

    brickset_index: BricksetIndex = get_brickset_index(my_index)
    print(brickset_index)
    print(separator)

    print(f"Minifigures: {brickset_index.tot_num_minifigs}")
    print(separator)

    print(f"Top-{top_n} theme:")
    for top_theme, freq in brickset_index.top_n_themes(top_n):
        print(f"{top_theme}: {freq}")
    print(separator)

    print(f"Total cost: {brickset_index.tot_rrp_available} €")
    print(separator)

    print(f"Top-{top_n} cost:")
    for top_set in brickset_index.top_n_rrp_eur(top_n):
        print(f"{top_set.num}: {top_set.name}: {top_set.rrp_eur} €")
    print(separator)

    print(f"Bottom-{top_n} price per piece:")
    for top_set in brickset_index.bottom_n_ppp_eur(top_n):
        print(f"{top_set.num}: {top_set.name}: {top_set.ppp_eur} c")
    print(separator)

    print(f"Top-{top_n} price per piece:")
    for top_set in brickset_index.top_n_ppp_eur(top_n):
        print(f"{top_set.num}: {top_set.name}: {top_set.ppp_eur} c")
    print(separator)

    print("By date:")
    for lego_set in sorted(my_index.sets, key=lambda s: s.year):
        print(f"{lego_set.num}: {lego_set.name}: {lego_set.year}")
    print(separator)


if __name__ == "__main__":
    explore()

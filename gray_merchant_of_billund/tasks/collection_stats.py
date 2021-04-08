import logging

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
from gray_merchant_of_billund.utils.log import get_logger
from gray_merchant_of_billund.utils.utils_resources import (
    get_personal_collection,
    get_personal_index,
    get_rebrickable_index,
)

log = get_logger(stdout_level=logging.DEBUG)


def collection_stats():
    separator = "-" * 25

    my_collection: CollectionIndex = get_personal_collection(
        # posix_path(RESOURCES_DIR, "autogen.txt")  # TODO: fix
    )
    rebrickable_index: RebrickableIndex = get_rebrickable_index()
    my_index: RebrickableIndex = get_personal_index(
        my_collection,
        rebrickable_index,
    )
    bricklink_index: BricklinkIndex = get_bricklink_index(my_index)
    brickset_index: BricksetIndex = get_brickset_index(my_index)
    correct_brickset_index(brickset_index)

    num_gifts: int = len([s for s in my_collection if s.gift])
    num_instructions: int = len([s for s in my_collection if s.instructions])
    print(f"Sets: {len(my_collection)} ({num_gifts} 🎁, {num_instructions} 📖)")
    print(my_collection)
    print(separator)

    print(f"Indexed sets ({len(my_index)}/{len(my_collection)})")
    if len(my_index) != len(my_collection):
        print("Missing sets:")
        print(
            "\n".join(
                f"{s.num}: {s.name}"
                for s in my_collection
                if s not in my_index
            )
        )

    print(f"Total parts: {my_index.tot_num_parts}")
    print(f"Avg set parts: {my_index.avg_num_parts:.2f}")
    print(f"Median set parts: {my_index.median_num_parts}")
    print(f"Minifigures: {brickset_index.tot_num_minifigs}")
    print(
        f"Total purchase price: {my_collection.tot_purchase_price:.2f} € "
        f"(paid: {my_collection.actually_paid_price:.2f} €, gift: "
        f"{my_collection.tot_purchase_price - my_collection.actually_paid_price:.2f} €)"
    )
    print(f"Total RRP price: {brickset_index.tot_rrp_available:.2f} €")
    print(
        f"Avg price per piece: {100 * my_collection.tot_purchase_price/my_index.tot_num_parts:.2f} c"
    )
    print(separator)

    # big_set_threshold = 999
    # print(f"Sets > {big_set_threshold} parts:")
    # for top_set in my_index.larger_than(big_set_threshold):
    #     print(
    #         f"{top_set.num}: {top_set.name} ({top_set.year}): {top_set.num_parts} parts"
    #     )
    # print(separator)

    top_n = 5
    print(f"Top-{top_n} num parts:")
    for top_set in my_index.top_n_large(top_n):
        print(
            f"{top_set.num}: {top_set.name} ({top_set.year}): {top_set.num_parts} parts"
        )
    print(separator)

    # print(bricklink_index)
    # print(separator)

    print(f"Top-{top_n} rarest:")
    for top_set in bricklink_index.top_n_rare(top_n):
        print(
            f"{top_set.num}: {top_set.name} ({top_set.year}): {top_set.for_sale} for sale"
        )
    print(separator)

    print(f"Top-{top_n} most wanted:")
    for top_set in bricklink_index.top_n_wanted(top_n):
        print(
            f"{top_set.num}: {top_set.name} ({top_set.year}): {top_set.on_wanted} wanted"
        )
    print(separator)

    print(brickset_index)
    print(separator)

    print(f"Top-{top_n} theme:")
    for top_theme, freq in brickset_index.top_n_themes(top_n):
        print(f"{top_theme}: {freq}")
    print(separator)

    print(f"Bottom-{top_n} RRP cost:")
    for top_set in brickset_index.bottom_n_rrp_eur(top_n):
        print(
            f"{top_set.num}: {top_set.name} ({top_set.year}): {top_set.rrp_eur} €"
        )
    print(separator)

    print(f"Top-{top_n} RRP cost:")
    for top_set in brickset_index.top_n_rrp_eur(top_n):
        print(
            f"{top_set.num}: {top_set.name} ({top_set.year}): {top_set.rrp_eur} €"
        )
    print(separator)

    print(f"Bottom-{top_n} RRP per piece:")
    for top_set in brickset_index.bottom_n_ppp_eur(top_n):
        print(
            f"{top_set.num}: {top_set.name} ({top_set.year}): {top_set.ppp_eur} c"
        )
    print(separator)

    print(f"Top-{top_n} RRP per piece:")
    for top_set in brickset_index.top_n_ppp_eur(top_n):
        print(
            f"{top_set.num}: {top_set.name} ({top_set.year}): {top_set.ppp_eur} c"
        )
    print(separator)

    prices_diff = []
    for lego_set in brickset_index:
        if not my_collection[lego_set.num].purchase_price:
            continue
        my_price = my_collection[lego_set.num].purchase_price
        if lego_set.rrp_eur is not None:
            prices_diff.append(
                (
                    lego_set,
                    my_price - lego_set.rrp_eur,
                    (my_price - lego_set.rrp_eur) * 100 / lego_set.rrp_eur,
                )
            )
        elif lego_set.rrp_usd is not None:
            prices_diff.append(
                (
                    lego_set,
                    my_price - lego_set.rrp_usd,
                    (my_price - lego_set.rrp_usd) * 100 / lego_set.rrp_usd,
                )
            )
        else:
            continue
    print(f"Top-{top_n} underpaid (absolute):")
    for top_set, top_diff, _ in sorted(prices_diff, key=lambda d: d[1])[
        :top_n
    ]:
        print(
            f"{top_set.num}: {top_set.name} ({top_set.year}): {top_diff:.2f} €"
        )
    print(separator)

    print(f"Top-{top_n} underpaid (relative):")
    for top_set, _, perc in sorted(prices_diff, key=lambda d: d[2])[:top_n]:
        print(f"{top_set.num}: {top_set.name} ({top_set.year}): {perc:.2f}%")
    print(separator)

    print(f"Top-{top_n} overpaid (absolute):")
    for top_set, top_diff, _ in sorted(
        prices_diff, key=lambda d: d[1], reverse=True
    )[:top_n]:
        print(
            f"{top_set.num}: {top_set.name} ({top_set.year}): {top_diff:.2f} €"
        )
    print(separator)

    print(f"Top-{top_n} overpaid (relative):")
    for top_set, _, perc in sorted(
        prices_diff, key=lambda d: d[2], reverse=True
    )[:top_n]:
        print(f"{top_set.num}: {top_set.name} ({top_set.year}): {perc:.2f}%")
    print(separator)

    balance: int = 0
    print(
        "Bricklink current used avg price (Purchase Price, absolute difference):"
    )
    for lego_set in bricklink_index:
        price_guide = lego_set.price_guide
        if price_guide.aggregate_current_used:
            avg_price = price_guide.aggregate_current_used.avg_price
            price_diff: float = (
                avg_price - my_collection[lego_set.num].purchase_price
            )
            print(
                f"{lego_set.num}: {lego_set.name} ({lego_set.year}): {avg_price} € "
                f"(PP: {my_collection[lego_set.num].purchase_price} €, "
                f"{price_diff:.2f} € {'💰' if price_diff > 0 else '💸'})"
            )
            balance += price_diff
        else:
            print(
                f"{lego_set.num}: {lego_set.name} ({lego_set.year}): nothing on the market right now!"
            )
    print(separator)
    total, missing = bricklink_index.total_current_used_avg_price
    print(
        f"Bricklink current used total avg price: {total:.2f} € ({len(missing)} sets missing)"
    )
    print(f"Balance: {balance:.2f} € {'💰' if balance > 0 else '💸'}")
    if len(missing) > 0:
        print("Missing sets:")
        for lego_set in missing:
            print(f"{lego_set.num}: {lego_set.name} ({lego_set.year})")
    print(separator)

    print(
        "Bricklink current new avg price (Purchase Price, absolute difference):"
    )
    balance = 0
    for lego_set in bricklink_index:
        price_guide = lego_set.price_guide
        if price_guide.aggregate_current_new:
            avg_price = price_guide.aggregate_current_new.avg_price
            price_diff: float = (
                avg_price - my_collection[lego_set.num].purchase_price
            )
            print(
                f"{lego_set.num}: {lego_set.name} ({lego_set.year}): {avg_price} € "
                f"(PP: {my_collection[lego_set.num].purchase_price} €, "
                f"{price_diff:.2f} € {'💰' if price_diff > 0 else '💸'})"
            )
            balance += price_diff
        else:
            print(
                f"{lego_set.num}: {lego_set.name} ({lego_set.year}): nothing on the market right now!"
            )
    print(separator)
    total, missing = bricklink_index.total_current_new_avg_price
    print(
        f"Bricklink current new total avg price: {total:.2f} € ({len(missing)} sets missing)"
    )
    print(f"Balance: {balance:.2f} € {'💰' if balance > 0 else '💸'}")
    if len(missing) > 0:
        print("Missing sets:")
        for lego_set in missing:
            print(f"{lego_set.num}: {lego_set.name} ({lego_set.year})")
    print(separator)

    # print(f"Missing € RRP:")
    # for lego_set in brickset_index:
    #     if lego_set.rrp_eur is None:
    #         print(lego_set)
    # print(separator)


def correct_brickset_index(brickset_index: BricksetIndex):
    for free_set in ["30472-1", "40335-1", "40370-1", "5006291-1", "40450-1"]:
        if free_set in brickset_index:
            brickset_index[free_set].rrp_raw = "£0 / $0 / 0€"


if __name__ == "__main__":
    collection_stats()

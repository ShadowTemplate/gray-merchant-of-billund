from typing import List

from gray_merchant_of_billund.constants.gmob import (
    BOOTSTRAP_FILE,
    RESOURCES_DIR,
)
from gray_merchant_of_billund.indexer.brickset_indexer import _get_brickset_set
from gray_merchant_of_billund.model.brickset_set import BricksetSet
from gray_merchant_of_billund.model.rebrickable_set import RebrickableIndex
from gray_merchant_of_billund.utils.path import posix_path
from gray_merchant_of_billund.utils.utils_resources import (
    get_rebrickable_index,
)


def bootstrap():
    sets: List[str] = []
    for line in open(BOOTSTRAP_FILE, "r"):
        if line.startswith("#") or line == '\n':
            continue
        sets.append(line.replace("\n", ""))
    rebrickable_index: RebrickableIndex = get_rebrickable_index()
    with open(posix_path(RESOURCES_DIR, "autogen.txt"), "w") as out_f:
        out_f.write(
            "# SET #   |"
            "SET NAME (YEAR)                                |"
            "PRICE €|"
            "PRICE NOTES      |"
            "ACQUIRED DATE|"
            "DATE NOTES      |"
            "GIFT|"
            "INSTRUCTIONS|"
            "ACQUIRED LOCATION                  |"
            "NEW|"
            "OTHER NOTES\n"
        )
        for lego_set in sets:
            set_num: str = f"{lego_set}-1"
            brickset_set: BricksetSet = _get_brickset_set(
                rebrickable_index[set_num]
            )
            set_name: str = rebrickable_index[set_num].name
            set_year: str = rebrickable_index[set_num].year
            full_name: str = f"{set_name} ({set_year})"
            # TODO: Guessed from RRP
            price: str = f"{brickset_set.rrp_available if brickset_set.rrp_available else ''}"
            price_notes: str = (
                "Guessed from RRP" if brickset_set.rrp_available else "Unknown"
            )
            acquired_date: str = f"31/12/{set_year}"
            date_notes: str = "Uncertain year"
            gift: str = ''
            instructions: str = ''
            acquired_location: str = ''
            acquired_new: str = ''
            out_f.write(
                f"{set_num:<10}|"
                f"{full_name:<47}|"
                f"{price:<7}|"
                f"{price_notes:<17}|"
                f"{acquired_date:<13}|"
                f"{date_notes:<16}|"
                f"{gift:<4}|"
                f"{instructions:<12}|"
                f"{acquired_location:<35}|"
                f"{acquired_new:<3}|\n"
            )


if __name__ == "__main__":
    bootstrap()

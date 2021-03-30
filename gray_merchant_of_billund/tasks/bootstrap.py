from typing import List

from gray_merchant_of_billund.constants.gmob import (
    BOOTSTRAP_FILE,
    RESOURCES_DIR,
)
from gray_merchant_of_billund.model.rebrickable_set import RebrickableIndex
from gray_merchant_of_billund.utils.path import posix_path
from gray_merchant_of_billund.utils.utils_resources import (
    get_rebrickable_index,
)


def bootstrap():
    sets: List[str] = []
    for line in open(BOOTSTRAP_FILE, "r"):
        if line.startswith("#"):
            continue
        sets.append(line.replace("\n", ""))
    rebrickable_index: RebrickableIndex = get_rebrickable_index()
    with open(posix_path(RESOURCES_DIR, "autogen.txt"), "w") as out_f:
        out_f.write(
            "# SET #   |"
            "SET NAME (YEAR)                                |"
            "PRICE €|"
            "PRICE NOTES            |"
            "ACQUIRED DATE|"
            "OTHER NOTES\n"
        )
        for lego_set in sets:
            set_num: str = f"{lego_set}-1"
            set_name: str = rebrickable_index[set_num].name
            set_year: str = rebrickable_index[set_num].year
            full_name: str = f"{set_name} ({set_year})"
            out_f.write(
                f"{set_num:<10}|{full_name:<47}|{'':<7}|{'':<23}|{'':<13}|\n"
            )


if __name__ == "__main__":
    bootstrap()

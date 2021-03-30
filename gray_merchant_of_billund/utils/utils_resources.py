import gzip
from typing import List, Optional, Sequence

from gray_merchant_of_billund.constants.gmob import (
    PERSONAL_COLLECTION_FIELDS_NUMBER,
    PERSONAL_COLLECTION_FIELDS_SEPARATOR,
    PERSONAL_COLLECTION_FILE,
    REBRICKABLE_SETS_CSV_FILE,
)
from gray_merchant_of_billund.model.base_set import BaseSet
from gray_merchant_of_billund.model.collection_set import (
    CollectionIndex,
    CollectionSet,
)
from gray_merchant_of_billund.model.rebrickable_set import (
    RebrickableIndex,
    RebrickableSet,
)
from gray_merchant_of_billund.utils.log import get_logger

log = get_logger()


def get_personal_collection(
    personal_collection_file: str = PERSONAL_COLLECTION_FILE,
) -> CollectionIndex:
    log.debug(
        f"Reading personal collection file {personal_collection_file}..."
    )
    sets: List[CollectionSet] = []
    for line_num, line in enumerate(open(personal_collection_file), start=1):
        if line.startswith("#") or line == "\n":
            continue

        fields: Sequence[str] = [
            f.strip(" ")
            for f in line.split(PERSONAL_COLLECTION_FIELDS_SEPARATOR)
        ]

        if len(fields) != PERSONAL_COLLECTION_FIELDS_NUMBER:
            raise ValueError(
                f"Incorrect number of fields in personal collection file "
                f"(expected {PERSONAL_COLLECTION_FIELDS_NUMBER}, "
                f"found {len(fields)})"
            )

        num: str = fields[0]
        name_year: str = fields[1]
        if "(" not in name_year or ")" not in name_year:
            raise ValueError(
                f"Missing (year) for set {num} at line {line_num} "
                f"in name '{name_year}'"
            )
        purchase_price: Optional[float] = None
        if fields[2] != "":
            purchase_price = float(fields[2])
        price_notes: Optional[str] = None
        if fields[3] != "":
            price_notes = fields[3]
        acquired_date: Optional[str] = None
        if fields[4] != "":
            acquired_date = fields[4].strip("\n")
        other_notes: Optional[str] = None
        if fields[5] != "":
            other_notes = fields[5].strip("\n")
        name: str = name_year[: name_year.rindex(" ")]
        year: str = name_year[
            name_year.rindex("(") + 1 : name_year.rindex(")")
        ]

        sets.append(
            CollectionSet(
                BaseSet(
                    num,
                    name,
                    year,
                ),
                purchase_price,
                price_notes,
                acquired_date,
                other_notes,
            )
        )
    return CollectionIndex(sets)


def get_rebrickable_index(
    rebrickable_sets_csv_file: str = REBRICKABLE_SETS_CSV_FILE,
) -> RebrickableIndex:
    with gzip.open(rebrickable_sets_csv_file, "rb") as f:
        file_content = f.read().decode("utf-8")

    sets: List[RebrickableSet] = []
    skip_header: bool = True
    for line in file_content.split("\n"):
        if skip_header or line == "":
            skip_header = False
            continue
        if line.count(",") == 4:
            num, name, year, theme_id, num_parts_str = line.split(",")
        else:
            # set name contains comma
            tokens: List[str] = line.split(",")
            num = tokens.pop(0)
            year = tokens.pop(-3)
            theme_id = tokens.pop(-2)
            num_parts_str = tokens.pop(-1)
            name = ",".join(tokens)[1:-1]
        num_parts = int(num_parts_str)
        sets.append(
            RebrickableSet(
                BaseSet(
                    num,
                    name,
                    year,
                ),
                theme_id,
                num_parts,
            )
        )
    return RebrickableIndex(sets)


def get_personal_index(
    my_collection: CollectionIndex,
    rebrickable_index: RebrickableIndex,
) -> RebrickableIndex:
    indexed_sets: List[RebrickableSet] = []
    for s in my_collection:
        if s.num not in rebrickable_index:
            log.warning(f"Missing set {s} in Rebrickable index. Skipping it.")
            continue
        rebrickable_set: RebrickableSet = rebrickable_index[s.num]
        indexed_sets.append(
            RebrickableSet(
                BaseSet(
                    s.num,
                    rebrickable_set.name,  # TODO: print warning if do not match with s.name
                    rebrickable_set.year,  # TODO: print warning if do not match with s.year
                ),
                rebrickable_set.theme_id,
                rebrickable_set.num_parts,
            )
        )
    return RebrickableIndex(indexed_sets)

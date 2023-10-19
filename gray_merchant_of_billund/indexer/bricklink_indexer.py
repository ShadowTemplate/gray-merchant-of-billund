import time
from typing import List, Optional

import requests
from pyquery import PyQuery  # type: ignore

from gray_merchant_of_billund.constants.gmob import (
    BRICKLINK_SET_SHOP_URL,
    BRICKLINK_SLEEP_TIMEOUT,
)
from gray_merchant_of_billund.indexer.bricklink_prices import get_price_guide
from gray_merchant_of_billund.model.bricklink_price import PriceGuide
from gray_merchant_of_billund.model.bricklink_set import (
    BricklinkIndex,
    BricklinkSet,
)
from gray_merchant_of_billund.model.exception import BricklinkQuotaError
from gray_merchant_of_billund.model.rebrickable_set import (
    RebrickableIndex,
    RebrickableSet,
)
from gray_merchant_of_billund.storage.expirable import load
from gray_merchant_of_billund.utils.log import get_logger
from gray_merchant_of_billund.utils.utils_request import execute_http_request

log = get_logger()


def get_bricklink_index(
    index: RebrickableIndex, time_to_live_ms: Optional[int] = None
) -> BricklinkIndex:
    sets: List[BricklinkSet] = []
    for lego_set in index:
        bricklink_set: Optional[BricklinkSet] = load(
            BricklinkSet, lego_set.store_key, time_to_live_ms
        )
        if not bricklink_set:
            bricklink_set = _get_bricklink_set(lego_set)
            bricklink_set.save()
            time.sleep(BRICKLINK_SLEEP_TIMEOUT)
        sets.append(bricklink_set)
    return BricklinkIndex(sets)


def _get_bricklink_set(lego_set: RebrickableSet) -> BricklinkSet:
    lego_set_url: str = BRICKLINK_SET_SHOP_URL.format(num=lego_set.num)
    log.info(f"Getting info from {lego_set_url}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux i686) "
        "AppleWebKit/537.17 (KHTML, like Gecko) "
        "Chrome/24.0.1312.27 "
        "Safari/537.17"
    }
    response = execute_http_request(
        requests.get,  # session.get
        lego_set_url,
        headers=headers,
    )
    pq = PyQuery(response.content)

    my_inventory = pq("#_idAddToMyInvLink").parent()
    try:
        for_sale = _parse_bricklink_info(my_inventory, "For Sale")
        log.debug(for_sale)  # X Lots For Sale
        for_sale = int(for_sale.split(" ")[0])
    except ValueError:  # TODO
        for_sale = 0

    my_wanted_list = pq("#_idAddToWantedLink").parent()
    try:
        on_wanted = _parse_bricklink_info(my_wanted_list, "Wanted Lists")
        log.debug(on_wanted)  # On X Wanted Lists
        on_wanted = int(on_wanted.split(" ")[1])
    except ValueError:  # TODO
        on_wanted = 0
    try:
        price_guide: PriceGuide = get_price_guide(
            lego_set.link_bricklink_set_history
        )
        price_guide_box: PriceGuide = get_price_guide(
            lego_set.link_bricklink_box_history
        )
    except BricklinkQuotaError:
        # handle soft-ban
        log.warning("Soft-banned. Sleeping...")
        time.sleep(BRICKLINK_SLEEP_TIMEOUT)
        return _get_bricklink_set(lego_set)
    return BricklinkSet(
        lego_set, for_sale, on_wanted, price_guide, price_guide_box
    )


def _parse_bricklink_info(block, key):
    info = str(next(block.items()))  # raw block
    lines = (l for l in info.split("\n") if key in l)
    try:
        info = next(lines)  # raw line
        info = info.lstrip("\t").rstrip("&#13;")
        info = info[len("<br/>") :]
        return info
    except StopIteration:
        raise ValueError()  # TODO: error

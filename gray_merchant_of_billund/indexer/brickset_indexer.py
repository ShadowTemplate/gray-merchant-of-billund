from typing import Dict, List, Optional

import requests
from pyquery import PyQuery  # type: ignore

from gray_merchant_of_billund.constants.gmob import (
    BRICKSET_FIELDS,
    BRICKSET_SET_URL,
)
from gray_merchant_of_billund.model.brickset_set import (
    BricksetIndex,
    BricksetSet,
)
from gray_merchant_of_billund.model.rebrickable_set import (
    RebrickableIndex,
    RebrickableSet,
)
from gray_merchant_of_billund.storage.expirable import load
from gray_merchant_of_billund.utils.log import get_logger
from gray_merchant_of_billund.utils.utils_request import execute_http_request

log = get_logger()


def get_brickset_index(
        index: RebrickableIndex, time_to_live_ms: Optional[int] = None
) -> BricksetIndex:
    sets: List[BricksetSet] = []
    for lego_set in index:
        brickset_set: Optional[BricksetSet] = load(
            BricksetSet, lego_set.store_key, time_to_live_ms
        )
        if not brickset_set:
            brickset_set = _get_brickset_set(lego_set)
            brickset_set.save()
        sets.append(brickset_set)
    return BricksetIndex(sets)


def _get_brickset_set(lego_set: RebrickableSet) -> BricksetSet:
    lego_set_url = BRICKSET_SET_URL.format(num=lego_set.num)
    log.debug(lego_set_url)
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
    }
    try:
        response = execute_http_request(
            requests.get, lego_set_url, headers=headers
        )
        pq = PyQuery(response.content)
        labels = [item.text for item in pq(".featurebox dl dt")]
        raw_values = [item for item in pq(".featurebox dl dd")]
        values = []
        for value in raw_values:
            if value.text is None:  # value is a link
                links = pq(value)("a")
                for link in links.items():
                    values.append(link.text())
                    break  # only get the first link
            else:
                values.append(value.text)
        info: Dict[str, str] = {
            label: value
            for label, value in zip(labels, values)
            if label in BRICKSET_FIELDS
        }
        return BricksetSet(
            lego_set,
            info.get("Theme", ""),
            int(info.get("Minifigs", "0")) if "Minifigs" in info else 0,
            info.get("Designer", ""),
            info.get("RRP", ""),
            info.get("Price per piece", ""),
            info.get("Dimensions", ""),
        )
    except Exception as exc:
        log.exception(
            "Unable to fetch data.\nPlease check your Internet connection and the availability of the site."
        )
        log.exception(
            f"Okay, merchant, we've had a problem here.\n{type(exc).__name__}: {str(exc)}"
        )
        raise exc

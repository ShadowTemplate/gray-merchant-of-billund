import time
from typing import List, Optional, Sequence

import requests
from pyquery import PyQuery  # type: ignore

from gray_merchant_of_billund.model.bricklink_price import (
    BricklinkAggregatePrices,
    BricklinkAggregateSelling,
    BricklinkAggregateSellingCurrent,
    BricklinkAggregateSold,
    BricklinkAggregateSoldMonth,
    BricklinkMarketEntry,
    PriceGuide,
)
from gray_merchant_of_billund.model.exception import BricklinkQuotaError
from gray_merchant_of_billund.utils.log import get_logger
from gray_merchant_of_billund.utils.utils_request import execute_http_request

log = get_logger()


def get_price_guide(lego_set_url) -> PriceGuide:
    log.debug(f"Processing history at {lego_set_url}...")
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

    if "Quota Exceeded" in pq.text():
        # handle soft-ban
        raise BricklinkQuotaError()

    aggregate_prices_fields = [
        "Total Qty:",
        "Min Price:",
        "Avg Price:",
        "Qty Avg Price:",
        "Max Price:",
    ]
    tds: Sequence[PyQuery] = list(pq("td").items())
    sales_summaries: List[Optional[PyQuery]] = []
    aggregate_availability_clues: List[PyQuery] = []
    for td in tds:
        td_str = str(td)
        if 'valign="TOP"' in td_str and "javascript" not in td_str:
            aggregate_availability_clues.append(td)
            if td.text() == "(Unavailable)":
                sales_summaries.append(None)
        if "colspan" in str(td) or 'valign="TOP"' in str(td):
            continue
        if any(field not in td_str for field in aggregate_prices_fields):
            continue
        sales_summaries.append(td)

    aggregate_last_6_months_new: Optional[BricklinkAggregateSold] = None
    if sales_summaries and sales_summaries[0]:
        aggregate_last_6_months_new = _parse_bricklink_aggregate_prices_sold(
            _get_td_lines(sales_summaries[0])
        )
    aggregate_last_6_months_used: Optional[BricklinkAggregateSold] = None
    if sales_summaries and sales_summaries[1]:
        aggregate_last_6_months_used = _parse_bricklink_aggregate_prices_sold(
            _get_td_lines(sales_summaries[1])
        )
    aggregate_current_new: Optional[BricklinkAggregateSelling] = None
    if sales_summaries and sales_summaries[2]:
        aggregate_current_new = _parse_bricklink_aggregate_prices_selling(
            _get_td_lines(sales_summaries[2])
        )
    aggregate_current_used: Optional[BricklinkAggregateSelling] = None
    if sales_summaries and sales_summaries[3]:
        aggregate_current_used = _parse_bricklink_aggregate_prices_selling(
            _get_td_lines(sales_summaries[3])
        )

    detailed_sales_new = []
    detailed_sales_used = []
    for td in tds:
        bgcolor = td.attr("bgcolor")
        if not bgcolor:
            continue
        if bgcolor == "EEEEEE":
            detailed_sales_new.append(td)
        if bgcolor == "DDDDDD":
            detailed_sales_used.append(td)

    details_last_6_months_new: Optional[
        Sequence[BricklinkAggregateSoldMonth]
    ] = None
    if sales_summaries and sales_summaries[0]:
        details_last_6_months_new = (
            _parse_bricklink_aggregate_prices_sold_months(
                _get_td_lines(detailed_sales_new[0])
            )
        )
    details_last_6_months_used: Optional[
        Sequence[BricklinkAggregateSoldMonth]
    ] = None
    if sales_summaries and sales_summaries[1]:
        details_last_6_months_used = (
            _parse_bricklink_aggregate_prices_sold_months(
                _get_td_lines(detailed_sales_used[0])
            )
        )

    details_current_new: Optional[BricklinkAggregateSellingCurrent] = None
    if sales_summaries and sales_summaries[2]:
        details_current_new = (
            _parse_bricklink_aggregate_prices_selling_current(
                _get_td_lines(detailed_sales_new[1])
            )
        )
    details_current_used: Optional[BricklinkAggregateSellingCurrent] = None
    if sales_summaries and sales_summaries[3]:
        details_current_used = (
            _parse_bricklink_aggregate_prices_selling_current(
                _get_td_lines(detailed_sales_used[1])
            )
        )

    return PriceGuide(
        aggregate_last_6_months_new,
        aggregate_last_6_months_used,
        aggregate_current_new,
        aggregate_current_used,
        details_last_6_months_new,
        details_last_6_months_used,
        details_current_new,
        details_current_used,
    )


def _get_td_lines(td):
    return td.text().replace("\xa0", " ").replace(",", "").split("\n")


def _parse_bricklink_aggregate_prices_sold(lines) -> BricklinkAggregateSold:
    _pop_or_fail(lines, "Times Sold:")
    times_sold: int = int(lines[0])
    lines.pop(0)

    return BricklinkAggregateSold(
        _parse_bricklink_aggregate_prices(lines),
        times_sold,
    )


def _parse_bricklink_aggregate_prices_selling(
    lines,
) -> BricklinkAggregateSelling:
    _pop_or_fail(lines, "Total Lots:")
    total_lots: int = int(lines[0])
    lines.pop(0)

    return BricklinkAggregateSelling(
        _parse_bricklink_aggregate_prices(lines),
        total_lots,
    )


def _parse_bricklink_aggregate_prices(lines) -> BricklinkAggregatePrices:
    _pop_or_fail(lines, "Total Qty:")
    total_qty: int = int(lines[0])
    lines.pop(0)

    _pop_or_fail(lines, "Min Price:")

    currency: str
    min_price_str: str
    currency, min_price_str = lines[0].split(" ")
    min_price: float = float(min_price_str)
    lines.pop(0)

    _pop_or_fail(lines, "Avg Price:")

    avg_price_str: str
    _, avg_price_str = lines[0].split(" ")
    avg_price: float = float(avg_price_str)
    lines.pop(0)

    _pop_or_fail(lines, "Qty Avg Price:")

    qty_avg_price_str: str
    _, qty_avg_price_str = lines[0].split(" ")
    qty_avg_price: float = float(qty_avg_price_str)
    lines.pop(0)

    _pop_or_fail(lines, "Max Price:")

    max_price_str: str
    _, max_price_str = lines[0].split(" ")
    max_price: float = float(max_price_str)
    lines.pop(0)

    return BricklinkAggregatePrices(
        total_qty,
        min_price,
        avg_price,
        qty_avg_price,
        max_price,
        currency,
    )


def _parse_bricklink_aggregate_prices_sold_months(
    lines,
) -> List[BricklinkAggregateSoldMonth]:
    months_aggregate: List[BricklinkAggregateSoldMonth] = []
    current_month_lines = []
    last_month_field: str = "Max Price:"
    last_field_found: bool = False
    for line in lines:
        current_month_lines.append(line)
        if last_field_found:
            months_aggregate.append(
                _parse_bricklink_aggregate_prices_sold_month(
                    current_month_lines
                )
            )
            last_field_found = False
            current_month_lines = []

        if line == last_month_field:
            last_field_found = True
    return months_aggregate


def _parse_bricklink_aggregate_prices_sold_month(
    lines,
) -> BricklinkAggregateSoldMonth:
    month: str
    year: str
    month, year = lines[0].split(" ")
    lines.pop(0)
    _pop_or_fail(lines, "Qty")
    _pop_or_fail(lines, "Each")

    entries: List[BricklinkMarketEntry] = []
    while lines and lines[0] != "Times Sold:":
        entries.append(_parse_bricklink_market_entry(lines[:2]))
        lines = lines[2:]
    month_aggregate: BricklinkAggregateSold = (
        _parse_bricklink_aggregate_prices_sold(lines)
    )
    return BricklinkAggregateSoldMonth(
        month_aggregate,
        month,
        year,
        entries,
    )


def _parse_bricklink_market_entry(lines) -> BricklinkMarketEntry:
    currency: str
    each_str: str
    currency, each_str = lines[1].split(" ")
    each: float = float(each_str)
    return BricklinkMarketEntry(
        int(lines[0]),
        each,
        currency,
    )


def _parse_bricklink_aggregate_prices_selling_current(
    lines,
) -> BricklinkAggregateSellingCurrent:
    now: int = int(round(time.time() * 1000))
    _pop_or_fail(lines, "Currently Available")
    _pop_or_fail(lines, "Qty")
    _pop_or_fail(lines, "Each")
    entries: List[BricklinkMarketEntry] = []
    while lines and lines[0] != "Total Lots:":
        entries.append(_parse_bricklink_market_entry(lines[:2]))
        lines = lines[2:]

    price_selling: BricklinkAggregateSelling = (
        _parse_bricklink_aggregate_prices_selling(lines)
    )
    return BricklinkAggregateSellingCurrent(
        price_selling,
        now,
        entries,
    )


def _pop_or_fail(values, head):
    if values[0] == head:
        values.pop(0)
    else:
        raise ValueError()  # TODO: improve

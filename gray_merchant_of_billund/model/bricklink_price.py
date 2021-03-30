import datetime
from typing import Optional, Sequence


class BricklinkAggregatePrices:
    def __init__(
        self,
        total_qty: int,
        min_price: float,
        avg_price: float,
        qty_avg_price: float,
        max_price: float,
        currency: str,
    ):
        self.total_qty: int = total_qty
        self.min_price: float = min_price
        self.avg_price: float = avg_price
        self.qty_avg_price: float = qty_avg_price
        self.max_price: float = max_price
        self.currency: str = currency

    def __str__(self):
        return (
            f"Total Qty: {self.total_qty}\n"
            f"Min Price: {self.currency} {self.min_price}\n"
            f"Avg Price: {self.currency} {self.avg_price}\n"
            f"Qty Avg Price: {self.currency} {self.qty_avg_price}\n"
            f"Max Price: {self.currency} {self.max_price}"
        )


class BricklinkAggregateSold(BricklinkAggregatePrices):
    def __init__(
        self,
        bricklink_aggregate_prices: BricklinkAggregatePrices,
        times_sold: int,
    ):
        super().__init__(
            bricklink_aggregate_prices.total_qty,
            bricklink_aggregate_prices.min_price,
            bricklink_aggregate_prices.avg_price,
            bricklink_aggregate_prices.qty_avg_price,
            bricklink_aggregate_prices.max_price,
            bricklink_aggregate_prices.currency,
        )
        self.times_sold: int = times_sold

    def __str__(self):
        return f"Times Sold: {self.times_sold}\n" f"{super().__str__()}"


class BricklinkAggregateSelling(BricklinkAggregatePrices):
    def __init__(
        self,
        bricklink_aggregate_prices: BricklinkAggregatePrices,
        total_lots: int,
    ):
        super().__init__(
            bricklink_aggregate_prices.total_qty,
            bricklink_aggregate_prices.min_price,
            bricklink_aggregate_prices.avg_price,
            bricklink_aggregate_prices.qty_avg_price,
            bricklink_aggregate_prices.max_price,
            bricklink_aggregate_prices.currency,
        )
        self.total_lots: int = total_lots

    def __str__(self):
        return f"Total Lots: {self.total_lots}\n" f"{super().__str__()}"


class BricklinkMarketEntry:
    def __init__(
        self,
        qty: int,
        each: float,
        currency: str,
    ):
        self.qty: int = qty
        self.each: float = each
        self.currency: str = currency

    def __str__(self):
        return f"{self.qty} {self.currency} {self.each}"


class BricklinkAggregateSoldMonth(BricklinkAggregateSold):
    def __init__(
        self,
        bricklink_aggregate_prices_sold: BricklinkAggregateSold,
        month: str,
        year: str,
        entries: Sequence[BricklinkMarketEntry],
    ):
        super().__init__(
            bricklink_aggregate_prices_sold,
            bricklink_aggregate_prices_sold.times_sold,
        )
        self.month: str = month
        self.year: str = year
        self.entries: Sequence[BricklinkMarketEntry] = entries

    def __str__(self):
        return (
            f"{self.month} {self.year}\n"
            + "\n".join(str(e) for e in self.entries)
            + f"\n\n{super().__str__()}"
        )


class BricklinkAggregateSellingCurrent(BricklinkAggregateSelling):
    def __init__(
        self,
        bricklink_aggregate_prices_selling: BricklinkAggregateSelling,
        date: int,
        entries: Sequence[BricklinkMarketEntry],
    ):
        super().__init__(
            bricklink_aggregate_prices_selling,
            bricklink_aggregate_prices_selling.total_lots,
        )
        self.date: int = date
        self.entries: Sequence[BricklinkMarketEntry] = entries

    def __str__(self):
        dt = datetime.datetime.fromtimestamp(self.date / 1000.0)
        return (
            f"Currently Available ({dt.strftime('%d-%m-%Y %H:%M:%S')})\n"
            + "\n".join(str(e) for e in self.entries)
            + f"\n\n{super().__str__()}"
        )


class PriceGuide:
    def __init__(
        self,
        aggregate_last_6_months_new: Optional[BricklinkAggregateSold],
        aggregate_last_6_months_used: Optional[BricklinkAggregateSold],
        aggregate_current_new: Optional[BricklinkAggregateSelling],
        aggregate_current_used: Optional[BricklinkAggregateSelling],
        details_last_6_months_new: Optional[
            Sequence[BricklinkAggregateSoldMonth]
        ],
        details_last_6_months_used: Optional[
            Sequence[BricklinkAggregateSoldMonth]
        ],
        details_current_new: Optional[BricklinkAggregateSellingCurrent],
        details_current_used: Optional[BricklinkAggregateSellingCurrent],
    ):
        self.aggregate_last_6_months_new: Optional[
            BricklinkAggregateSold
        ] = aggregate_last_6_months_new
        self.aggregate_last_6_months_used: Optional[
            BricklinkAggregateSold
        ] = aggregate_last_6_months_used
        self.aggregate_current_new: Optional[
            BricklinkAggregateSelling
        ] = aggregate_current_new
        self.aggregate_current_used: Optional[
            BricklinkAggregateSelling
        ] = aggregate_current_used
        self.details_last_6_months_new: Optional[
            Sequence[BricklinkAggregateSoldMonth]
        ] = details_last_6_months_new
        self.details_last_6_months_used: Optional[
            Sequence[BricklinkAggregateSoldMonth]
        ] = details_last_6_months_used
        self.details_current_new: Optional[
            BricklinkAggregateSellingCurrent
        ] = details_current_new
        self.details_current_used: Optional[
            BricklinkAggregateSellingCurrent
        ] = details_current_used

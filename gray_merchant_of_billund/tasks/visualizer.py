import calendar
import math
import os
from collections import defaultdict
from datetime import date
from typing import List

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from gray_merchant_of_billund.constants.gmob import PLOT_DIR
from gray_merchant_of_billund.indexer.brickset_indexer import (
    get_brickset_index,
)
from gray_merchant_of_billund.model.base_set import BaseSet
from gray_merchant_of_billund.model.bricklink_set import BricklinkSet
from gray_merchant_of_billund.model.brickset_set import BricksetIndex
from gray_merchant_of_billund.model.collection_set import CollectionIndex
from gray_merchant_of_billund.model.rebrickable_set import RebrickableIndex
from gray_merchant_of_billund.storage.expirable import load_all
from gray_merchant_of_billund.utils.utils_resources import (
    get_personal_collection,
    get_personal_index,
    get_rebrickable_index,
)


def get_aggregate_sold_monthly_recap(set_num, dates, years):
    base_set = BaseSet(set_num, "UNKNOWN_NAME", "UNKNOWN_YEAR")
    bricklink_sets: List[BricklinkSet] = load_all(BricklinkSet, base_set.num)
    if len(bricklink_sets) < 1:
        raise ValueError(f"No data for set {base_set.num}")
    base_set.name = bricklink_sets[0].name
    base_set.year = bricklink_sets[0].year
    aggregate_sold_month_by_year_month_used = defaultdict(
        lambda: defaultdict(list)
    )
    aggregate_sold_month_by_year_month_new = defaultdict(
        lambda: defaultdict(list)
    )
    for set_snapshot in bricklink_sets:
        if set_snapshot.price_guide.details_last_6_months_used:
            # not sure how/why it's possible, but it's possible: deal with it
            for asm in set_snapshot.price_guide.details_last_6_months_used:
                aggregate_sold_month_by_year_month_used[asm.year][
                    asm.month
                ].append(asm)
        if set_snapshot.price_guide.details_last_6_months_new:
            # not sure how/why it's possible, but it's possible: deal with it
            for asm in set_snapshot.price_guide.details_last_6_months_new:
                aggregate_sold_month_by_year_month_new[asm.year][
                    asm.month
                ].append(asm)

    month_names = list(calendar.month_name)[1:]
    best_aggregate_sold_month_by_year_month_used = defaultdict(
        lambda: defaultdict(list)
    )
    best_aggregate_sold_month_by_year_month_new = defaultdict(
        lambda: defaultdict(list)
    )
    values_used = []
    values_new = []
    for year in years:
        year = str(year)
        for month in month_names:
            asms_used = aggregate_sold_month_by_year_month_used[year][month]
            asms_new = aggregate_sold_month_by_year_month_new[year][month]
            best_aggregate_sold_month_by_year_month_used[year][month] = []
            best_aggregate_sold_month_by_year_month_new[year][month] = []
            value = None
            if len(asms_used) > 0:
                best_asm = max(asms_used, key=lambda x: x.times_sold)
                best_aggregate_sold_month_by_year_month_used[year][
                    month
                ] = best_asm
                value = best_asm.qty_avg_price
            values_used.append(value)
            value = None
            if len(asms_new) > 0:
                best_asm = max(asms_new, key=lambda x: x.times_sold)
                best_aggregate_sold_month_by_year_month_new[year][
                    month
                ] = best_asm
                value = best_asm.qty_avg_price
            values_new.append(value)

    df = pd.DataFrame(
        {
            "Average price (new)": values_new,
            "Average price (used)": values_used,
        }
    )
    df = df.set_index(dates)
    # print(df)
    return base_set, df


def plot_asms(
    base_set, df, dates, purchase_price, purchase_date, retail_price, new=False
):
    months = mdates.MonthLocator()
    years_fmt = mdates.DateFormatter("%Y-%m")
    fig, axes = plt.subplots(figsize=(20, 7))
    axes.set(ylabel="Average price (€)")
    lines = df.shape[-1]
    palette = sns.color_palette("deep")[:lines]
    graph = sns.lineplot(data=df, marker="o", palette=palette)
    graph.set(title=str(base_set))
    plt.legend(loc="upper left")
    try:
        max_y = max(df.max())
        min_y = min(df.min())
        n_percent = abs(max_y - min_y) * 4 / 100
        offset = n_percent
    except TypeError:
        offset = 10

    # add purchase info
    color = palette[0] if new else palette[1]
    linestyle = "-" if new else "--"
    graph.axhline(purchase_price, color=color, linestyle=linestyle)
    plt.scatter(x=purchase_date, y=purchase_price, color=color, marker="x")
    plt.text(
        x=purchase_date,
        y=purchase_price - offset,
        s="{: .0f}".format(purchase_price),
        color=color,
    )

    # add retail info
    if retail_price:
        graph.axhline(retail_price, color="y")
        plt.text(
            x=dates[
                -1
            ],  # TODO: fix: sometimes it's too much on the right, out of plot
            y=retail_price - offset,
            s="{: .0f}".format(retail_price),
            color="y",
        )

    # label points on the plot
    # TODO: improve, generalizing to N columns
    for x, y in zip(dates, df["Average price (used)"]):
        if not y or math.isnan(y):
            continue
        plt.text(x=x, y=y - offset, s="{: .0f}".format(y))
    for x, y in zip(dates, df["Average price (new)"]):
        if not y or math.isnan(y):
            continue
        plt.text(x=x, y=y - offset, s="{: .0f}".format(y))

    axes.xaxis.set_major_locator(months)
    axes.xaxis.set_major_formatter(years_fmt)
    axes.xaxis.set_minor_locator(months)

    plt.xticks(rotation="vertical")
    # plt.show()
    plt.savefig(f"{PLOT_DIR}/{base_set.num}_{base_set.name}.png")
    plt.close()


def main():
    matplotlib.use("TkAgg")
    os.makedirs(PLOT_DIR, exist_ok=True)
    current_year = date.today().year
    my_collection: CollectionIndex = get_personal_collection()
    rebrickable_index: RebrickableIndex = get_rebrickable_index()
    my_index: RebrickableIndex = get_personal_index(
        my_collection,
        rebrickable_index,
    )
    start_year = current_year - 5  # only plot latest 10 years
    brickset_index: BricksetIndex = get_brickset_index(my_index)
    for s in my_collection:
        dates = pd.date_range(
            start=f"{start_year}-01-01",
            end=f"{current_year}-12-01",  # TODO: improve by stopping at current month
            freq="MS",
        )
        years = range(start_year, current_year + 1)
        my_set = s
        s = my_set.num
        base_set, df = get_aggregate_sold_monthly_recap(s, dates, years)
        _, month, year = my_set.acquired_date.split("/")
        try:
            rounded_date = [
                d for d in dates if str(d).startswith(f"{year}-{month}")
            ][0]
        except IndexError:
            rounded_date = dates[0]
        retail_price = brickset_index[s].rrp_available
        print(f"Generating plot for {base_set}...")
        plot_asms(
            base_set,
            df,
            dates,
            my_set.purchase_price,
            rounded_date,
            retail_price,
            new=my_set.acquired_new,
        )
        # continue


if __name__ == "__main__":
    main()

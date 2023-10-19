from collections import Counter
from pathlib import Path
from typing import Dict, Generator, Optional, Sequence, Tuple

from gray_merchant_of_billund.constants.gmob import MUTABLE_STORAGE_DIR
from gray_merchant_of_billund.model.rebrickable_set import (
    RebrickableIndex,
    RebrickableSet,
)
from gray_merchant_of_billund.storage.expirable import Expirable
from gray_merchant_of_billund.utils.time import now


class BricksetSet(RebrickableSet, Expirable):
    def __init__(
        self,
        rebrickable_lego_set: RebrickableSet,
        theme: str,
        num_minifigs: int,
        designer: str,
        rrp_raw: str,
        ppp_raw: str,
        dimensions: str,
    ):
        super().__init__(
            rebrickable_lego_set,
            rebrickable_lego_set.theme_id,
            rebrickable_lego_set.num_parts,
        )
        self.theme: str = theme
        self.num_minifigs: int = num_minifigs
        self.designer: str = designer
        self.rrp_raw: str = rrp_raw
        self.ppp_raw: str = ppp_raw
        self.dimensions: str = dimensions
        self._now: int = now()

    @property
    def rrp_gbp(self) -> Optional[float]:
        # self.rrp_raw is a string of the form:
        # £369.99 / $399.99 / 399.99€
        # TODO: handle case with no space, like for rrp_eur
        if self.rrp_raw is None or "£" not in self.rrp_raw:
            return None
        price: str = self.rrp_raw.split("£")[1]  # 369.99 / $399.99 / 399.99€
        price = price.rsplit(" ")[-1]  # 369.99
        return float(price)

    @property
    def rrp_usd(self) -> Optional[float]:
        # self.rrp_raw is a string of the form:
        # £369.99 / $399.99 / 399.99€
        # TODO: handle case with no space, like for rrp_eur
        if self.rrp_raw is None or "$" not in self.rrp_raw:
            return None
        price: str = self.rrp_raw.split("$")[1]  # 399.99 / 399.99€
        price = price.split(" ")[0]  # 399.99
        return float(price)

    @property
    def rrp_eur(self) -> Optional[float]:
        # self.rrp_raw is a string of the form:
        # £29.99/$39.99/€34.99
        # or
        # £34.99 / $34.99 / 49.99€
        if self.rrp_raw is None or "€" not in self.rrp_raw:
            return None
        price: str = self.rrp_raw.split("€")[1]  # £29.99/$39.99/€34.99
        if price == "":
            price: str = self.rrp_raw.split("€")[0]  # £34.99 / $34.99 / 49.99€
            price = price.rsplit(" ")[-1]
        return float(price)

    @property
    def rrp_available(self) -> Optional[float]:
        # priority: € > $ > £
        if self.rrp_eur is not None:
            return self.rrp_eur
        if self.rrp_usd is not None:
            return self.rrp_usd
        # too much difference: better skip
        # if self.rrp_gbp:
        #     return self.rrp_gbp
        return None

    @property
    def ppp_eur(self) -> Optional[float]:
        # self.ppp_raw is a string of the form:
        # 6.7p / 7.2c / 7.2c
        # or
        # 6.7p/8.2c/7.7c
        # so we assume € is the last price
        if self.ppp_raw is None or "c" not in self.ppp_raw:
            return None
        price: str = self.ppp_raw.split(" ")
        if len(price) > 1:  # 6.7p / 7.2c / 7.2c
            price = price[-1][:-1]
        else:  # 6.7p/8.2c/7.7c
            price = self.ppp_raw.split("/")[-1][:-1]
        return float(price)

    @staticmethod
    def store_dir() -> str:
        return (Path(MUTABLE_STORAGE_DIR) / "BricksetSet").as_posix()

    @property
    def creation_date_ms(self) -> int:
        return self._now

    def __str__(self):
        return (
            f"{super().__str__()} "
            f"Theme: {self.theme} "
            f"|Minifigs|: {self.num_minifigs} "
            f"Designer: {self.designer} "
            f"RRP: {self.rrp_raw} "
            f"PPP: {self.ppp_raw} "
            f"Dimensions: {self.dimensions}"
        )


class BricksetIndex(RebrickableIndex):
    def __init__(self, sets: Sequence[BricksetSet]):
        super().__init__(sets)
        self.sets: Sequence[BricksetSet] = sets
        self._index: Dict[str, int] = {
            lego_set.num: index for index, lego_set in enumerate(self.sets)
        }

    def __iter__(self) -> Generator[BricksetSet, None, None]:
        index: int = 0
        while index < self.size:
            yield self.sets[index]
            index += 1

    @property
    def tot_num_minifigs(self) -> int:
        return sum(s.num_minifigs for s in self.sets if s.num_minifigs)

    @property
    def tot_rrp_eur(self) -> float:
        return sum(s.rrp_eur for s in self.sets if s.rrp_eur)

    @property
    def tot_rrp_available(self) -> float:
        return sum(s.rrp_available for s in self.sets if s.rrp_available)

    @property
    def themes_index(self) -> int:
        return sum(s.num_minifigs for s in self.sets if s.num_minifigs)

    def top_n_themes(self, n: int) -> Sequence[Tuple[str, int]]:
        return Counter(s.theme for s in self.sets if s.theme).most_common(n)

    def bottom_n_rrp_eur(self, n: int) -> Sequence[BricksetSet]:
        return sorted(
            (s for s in self.sets if s.rrp_eur is not None),
            key=lambda s: s.rrp_eur if s.rrp_eur is not None else 0,
        )[:n]

    def top_n_rrp_eur(self, n: int) -> Sequence[BricksetSet]:
        return sorted(
            (s for s in self.sets if s.rrp_eur is not None),
            key=lambda s: -s.rrp_eur if s.rrp_eur is not None else 0,
        )[:n]

    def bottom_n_ppp_eur(self, n: int) -> Sequence[BricksetSet]:
        return sorted(
            (s for s in self.sets if s.ppp_eur is not None),
            key=lambda s: s.ppp_eur if s.ppp_eur is not None else 0,
        )[:n]

    def top_n_ppp_eur(self, n: int) -> Sequence[BricksetSet]:
        return sorted(
            (s for s in self.sets if s.ppp_eur is not None),
            key=lambda s: -s.ppp_eur if s.ppp_eur is not None else 0,
        )[:n]

import errno
import os
import pickle
from abc import abstractmethod
from glob import glob
from pathlib import Path
from typing import List, Optional, Type, TypeVar

from gray_merchant_of_billund.storage.saveable import Saveable
from gray_merchant_of_billund.utils.log import get_logger
from gray_merchant_of_billund.utils.time import now, pretty_str

log = get_logger()
TExpirable = TypeVar("TExpirable", bound="Expirable")


class Expirable(Saveable):
    @property
    @abstractmethod
    def creation_date_ms(self) -> int:
        pass

    def is_expired(self, time_to_live_ms: int) -> bool:
        return self.creation_date_ms + time_to_live_ms < now()

    @property
    def store_path(self) -> str:
        return Saveable.build_store_path(
            self.store_dir(),
            f"{self.creation_date_ms} ({pretty_str(self.creation_date_ms)})",
            store_sub_dir=self.store_key,
        )

    def save(self) -> None:
        log.debug(f"Saving item to {self.store_path}...")
        expirable_dir = Path(self.store_path).parent.as_posix()
        os.makedirs(expirable_dir, exist_ok=True)
        with open(self.store_path, "wb") as out_f:
            pickle.dump(self, out_f)
        log.debug(f"Saved item to {self.store_path}.")
        # make a symlink for fast retrieval
        latest = (Path(expirable_dir) / "latest.pkl").as_posix()
        log.debug(f"Making latest symlink to {latest}...")
        try:
            os.remove(latest)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise exc
        os.symlink(self.store_path, latest)
        log.debug(f"Made latest symlink to {latest}.")


def load(
    cls: Type[TExpirable], store_key: str, time_to_live_ms: Optional[int]
) -> Optional[TExpirable]:
    store_path: str = Expirable.build_store_path(
        cls.store_dir(),
        "latest",
        store_sub_dir=store_key,
    )
    log.debug(f"Loading item from {store_path}...")
    os.makedirs(cls.store_dir(), exist_ok=True)
    item: Optional[TExpirable] = None
    try:
        with open(store_path, "rb") as in_f:
            item = pickle.load(in_f)
            log.debug(f"Loaded item from {store_path}.")
            if (
                time_to_live_ms is not None
                and item
                and item.is_expired(time_to_live_ms)
            ):
                log.debug(f"Expired cache for {item}. Ignoring hit.")
                item = None
    except FileNotFoundError:
        log.debug(f"Missing item {store_path}.")
    finally:
        return item


def load_all(
    cls: Type[TExpirable],
    store_key: str,
) -> List[TExpirable]:
    store_path: str = Expirable.build_store_path(
        cls.store_dir(),
        "*",
        store_sub_dir=store_key,
    )
    log.debug(f"Loading items from {store_path}...")
    os.makedirs(cls.store_dir(), exist_ok=True)
    items: List[TExpirable] = []
    for store_path in (
        f for f in glob(store_path) if not f.endswith("latest.pkl")
    ):
        try:
            with open(store_path, "rb") as in_f:
                items.append(pickle.load(in_f))
                log.debug(f"Loaded item from {store_path}.")
        except FileNotFoundError:
            log.debug(f"Missing item {store_path}.")
    return items

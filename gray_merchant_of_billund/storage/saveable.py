import os
import pickle
from abc import ABCMeta, abstractmethod
from typing import Optional, Type, TypeVar

from gray_merchant_of_billund.utils.log import get_logger
from gray_merchant_of_billund.utils.path import posix_path

log = get_logger()
TSaveable = TypeVar("TSaveable", bound="Saveable")


class Saveable(metaclass=ABCMeta):
    @property
    @abstractmethod
    def store_key(self) -> str:
        pass

    @staticmethod
    @abstractmethod
    def store_dir() -> str:
        pass

    @staticmethod
    def build_store_path(store_dir, store_key, store_sub_dir="") -> str:
        return posix_path(store_dir, store_sub_dir, f"{store_key}.pkl")

    @property
    def store_path(self) -> str:
        return Saveable.build_store_path(self.store_dir(), self.store_key)

    def save(self) -> None:
        log.debug(f"Saving item to {self.store_path}...")
        os.makedirs(self.store_dir(), exist_ok=True)
        with open(self.store_path, "wb") as out_f:
            pickle.dump(self, out_f)
        log.debug(f"Saved item to {self.store_path}.")


def load(cls: Type[TSaveable], store_key: str) -> Optional[TSaveable]:
    store_path: str = Saveable.build_store_path(cls.store_dir(), store_key)
    log.debug(f"Loading item from {store_path}...")
    os.makedirs(cls.store_dir(), exist_ok=True)
    item: Optional[TSaveable] = None
    try:
        with open(store_path, "rb") as in_f:
            item = pickle.load(in_f)
            log.debug(f"Loaded item from {store_path}.")
    except FileNotFoundError:
        log.debug(f"Missing item {store_path}.")
    finally:
        return item

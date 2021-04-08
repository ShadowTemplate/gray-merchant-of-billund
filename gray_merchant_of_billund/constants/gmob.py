from pathlib import Path

from gray_merchant_of_billund.utils.path import posix_path

HOME = Path.home().as_posix()
APPLICATION_NAME = "GMoB"

APPLICATION_DIR = posix_path(HOME, APPLICATION_NAME)

RESOURCES_DIR = posix_path(APPLICATION_DIR, "resources")

REBRICKABLE_SETS_CSV_FILE = posix_path(RESOURCES_DIR, "sets.csv.gz")
PERSONAL_COLLECTION_FILE = posix_path(RESOURCES_DIR, "personal_collection.txt")
BOOTSTRAP_FILE = posix_path(RESOURCES_DIR, "bootstrap.txt")

CACHE_DIR = posix_path(APPLICATION_DIR, "cache")
IMMUTABLE_STORAGE_DIR = posix_path(CACHE_DIR, "immutable")
MUTABLE_STORAGE_DIR = posix_path(CACHE_DIR, "mutable")

PERSONAL_COLLECTION_FIELDS_SEPARATOR = "|"
PERSONAL_COLLECTION_FIELDS_NUMBER = 9

BRICKLINK_URL = "https://www.bricklink.com/"
BRICKLINK_SET_SHOP_URL = BRICKLINK_URL + "v2/catalog/catalogitem.page?S={num}"
BRICKLINK_SET_HISTORY_URL = BRICKLINK_URL + "catalogPG.asp?S={num}-"
BRICKLINK_SET_HISTORY_COMPLETE_URL = (
    BRICKLINK_SET_HISTORY_URL + "&viewExclude=Y"
)

BRICKSET_URL = "https://brickset.com/"
BRICKSET_SET_URL = BRICKSET_URL + "sets/{num}/"
BRICKSET_FIELDS = [
    "Theme",
    "Minifigs",
    "Designer",
    "RRP",
    "Price per piece",
    "Dimensions",
]

LEGO_SET_SHOP_URL = "https://www.lego.com/product/{shortnum}"

DEFAULT_DATE_FORMAT = "%d-%m-%Y, %H:%M:%S"

from os import PathLike
from pathlib import Path

from loguru import logger

from expense_report.enums import AccountType


class Config:
    config_path = None
    config = None

    @classmethod
    def get_paths_account_files(cls):
        if cls.config is None:
            return {}
        key = "path_and_account_files"
        if key in cls.config:
            return cls.config[key]
        else:
            return paths_account_files

    @classmethod
    def get_categories_and_keywords(cls):
        if cls.config is None:
            return {}
        key = "categories_and_keywords"
        if key in cls.config:
            return cls.config[key]
        else:
            return categories_and_keywords

    @classmethod
    def set_config_path(cls, config_path: str | PathLike):
        if config_path is not None:
            logger.info(
                f"Config path already set. Updating it to {str(cls.config_path)}"
            )

        cls.config_path = config_path


base_path = Path("/tmp")

paths_account_files = {
    "post": {"account_type": AccountType.post_finance, "path": base_path / "Post"},
    "neon": {"account_type": AccountType.neon, "path": base_path / "neon"},
    "cembra": {"account_type": AccountType.cembra, "path": base_path / "KK Cembra"},
}

categories_and_keywords = {
    "tanken": [
        "migrol",
    ],
    "lebensmittel/haushalt": [
        "migros",
        "aldi",
        "lidl",
        "coop",
        "denner",
        "volg" "migrolino",
        "kiosk",
        "landi",
        "jumbo",
    ],
    "medikamente": ["apotheke", "aptheke", "amavita"],
    "restaurant": ["mcdonalds", "pizza", "gasthof", "ristorante" "brezelkönig"],
}

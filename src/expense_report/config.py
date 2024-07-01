from os import PathLike

from loguru import logger


class Config:
    config_path = None
    config = None

    @classmethod
    def get_paths_account_files(cls):
        key = "path_and_account_files"
        if key in cls.config:
            return cls.config[key]
        else:
            return {}

    @classmethod
    def get_categories_and_keywords(cls):
        key = "categories_and_keywords"
        if key in cls.config:
            return cls.config[key]
        else:
            return {}

    @classmethod
    def set_config_path(cls, config_path: str | PathLike):
        if config_path is not None:
            logger.info(
                f"Config path already set. Updating it to {str(cls.config_path)}"
            )

        cls.config_path = config_path

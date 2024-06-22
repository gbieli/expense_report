from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ColumnNames:
    shop_date: str
    charge: str
    credit: str
    transaction_description: str
    data_origin: str


class Extractor(ABC):
    """
    This is the data file extractor base class. An extractor is responsible to extract
    the data from one file of a certain type of account
    """

    column_names: ColumnNames

    @abstractmethod
    def to_data_frame(self):
        pass

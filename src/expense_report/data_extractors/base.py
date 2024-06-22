from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


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
    file_type: str

    def __init__(self, pdf_file_path: Path):
        self.file_path = pdf_file_path
        self.file_name = self.file_path.name

    @abstractmethod
    def to_data_frame(self):
        pass

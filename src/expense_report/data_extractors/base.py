from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from pandas import DataFrame


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

    def _insert_convert(self, df: DataFrame, date_format: str):
        # insert new column with filename
        df.insert(1, self.column_names.data_origin, self.file_name)
        # convert to date
        df[self.column_names.shop_date] = pd.to_datetime(
            df[self.column_names.shop_date], format=date_format
        )
        df = df.sort_values(by=self.column_names.shop_date)
        # convert number columns
        number_columns = [self.column_names.charge, self.column_names.credit]
        for number_column in number_columns:
            df[number_column] = pd.to_numeric(
                df[number_column].astype(str).str.replace("'", ""), errors="coerce"
            )
        return df

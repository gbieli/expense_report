from enum import Enum
from pathlib import Path

import pandas as pd
from loguru import logger

from expense_report.categorize_functions import beschreibung_category
from expense_report.data_extractors.csv import NeonCSVFileExtractor
from expense_report.data_extractors.pdf import CembraPDFFileExtractor


class AccountTypes(Enum):
    cembra = CembraPDFFileExtractor
    neon = NeonCSVFileExtractor


class Account:
    """
    Represents an account which has a certain type.
    """

    account_type: AccountTypes

    def __init__(self, identifier: str, path: Path, excel_file_path: Path):
        self.identifier = identifier
        self.file_extractor_type = self.account_type.value
        self.path = path
        self.excel_file_path = excel_file_path

    @staticmethod
    def get_account_instance(
        account_type: AccountTypes, identifier: str, path: Path, excel_file_path: Path
    ):
        for subclass in Account.__subclasses__():
            if subclass.account_type.name == account_type:
                return subclass(identifier, path, excel_file_path)

    def generate_excel(
        self,
    ):
        df_list = []
        data_files = list(self.path.glob(f"*.{self.file_extractor_type.file_type}"))
        for file_path in data_files:
            df_from_file = self.file_extractor_type(file_path).to_data_frame()
            df_list.append(df_from_file)
        df = pd.concat(df_list)
        df["Jahr"] = df[self.file_extractor_type.column_names.shop_date].dt.year
        df["Wochentag"] = df[
            self.file_extractor_type.column_names.shop_date
        ].dt.day_name()
        df["Kategorie"] = df[
            self.file_extractor_type.column_names.transaction_description
        ].apply(beschreibung_category)
        df_pivot_beschreibung = df.pivot_table(
            values=self.file_extractor_type.column_names.charge,
            index=self.file_extractor_type.column_names.transaction_description,
            columns="Jahr",
            aggfunc="sum",
            fill_value=0.0,
        )
        df_pivot_kategorie = df.pivot_table(
            values=self.file_extractor_type.column_names.charge,
            index="Kategorie",
            columns="Jahr",
            aggfunc="sum",
            fill_value=0.0,
        )
        logger.info(f"Resulting dataframe: {str(df)}")

        # Write dataframe to excel
        logger.info(f"Generating Excel file at '{self.excel_file_path}'")
        with pd.ExcelWriter(self.excel_file_path) as writer:
            df.to_excel(writer, sheet_name=str(self.account_type.name))
            df_pivot_beschreibung.to_excel(writer, sheet_name="pivot_beschreibung")
            df_pivot_kategorie.to_excel(writer, sheet_name="pivot_kategorie")


class CembraAccount(Account):
    account_type = AccountTypes.cembra


class NeonAccount(Account):
    account_type = AccountTypes.neon

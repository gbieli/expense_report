import pandas as pd
from loguru import logger

from expense_report.data_extractors.base import ColumnNames, Extractor


class CSVFileExtractor(Extractor):
    column_names: ColumnNames
    file_type = "csv"
    separator: str


class NeonCSVFileExtractor(CSVFileExtractor):
    column_names = ColumnNames(
        shop_date="Date",
        charge="Charge",
        credit="Credit",
        transaction_description="Description",
        data_origin="Datenherkunft",
    )
    separator = ";"

    def to_data_frame(self):
        df = pd.read_csv(self.file_path, sep=self.separator)
        # combine description and subject columns
        df["Subject"] = df["Subject"].fillna("")
        df[self.column_names.transaction_description] = (
            df[self.column_names.transaction_description] + " " + df["Subject"]
        )
        df = df.drop("Subject", axis=1)
        amount_column_name = "Amount"
        # copy column
        df[self.column_names.charge] = df[amount_column_name]
        # set positive values in charge column to 0
        df.loc[df[self.column_names.charge] >= 0, self.column_names.charge] = 0
        # convert negative values in charge column to positive values
        df[self.column_names.charge] = df[self.column_names.charge].abs()
        # set negative values in amount column to 0
        df.loc[df[amount_column_name] < 0, amount_column_name] = 0
        # rename amount column to credit column
        df = df.rename(columns={amount_column_name: self.column_names.credit})
        # insert and convert
        df = self._insert_convert(df, "%Y-%m-%d")
        logger.info(f"{self.file_name}: data frame {str(df)}")
        return df

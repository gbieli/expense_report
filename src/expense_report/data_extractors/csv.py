from expense_report.data_extractors.base import Extractor, ColumnNames
import pandas as pd
from loguru import logger


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
        amount_column_name = "Amount"
        df[self.column_names.charge] = df[amount_column_name]
        df.loc[df[self.column_names.charge] >= 0, self.column_names.charge] = 0
        df[self.column_names.charge] = df[self.column_names.charge].abs()
        df.loc[df[amount_column_name] < 0, amount_column_name] = 0
        df = df.rename(columns={amount_column_name: self.column_names.credit})
        df = self._insert_convert(df, "%Y-%m-%d")
        logger.info(f"{self.file_name}: data frame {str(df)}")
        return df

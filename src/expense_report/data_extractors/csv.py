from expense_report.data_extractors.base import Extractor, ColumnNames
import pandas as pd
from loguru import logger


class CSVFileExtractor(Extractor):
    column_names: None
    file_type = "csv"
    separator: str

    def to_data_frame(self):
        df = pd.read_csv(self.file_path, sep=self.separator)
        logger.info(f"{self.file_name}: data frame {str(df)}")
        return df


class NeonCSVFileExtractor(CSVFileExtractor):
    column_names = ColumnNames(
        shop_date="Date",
        charge="Amount",
        credit="Amount",
        transaction_description="Description",
        data_origin="Datenherkunft",
    )
    separator = ";"

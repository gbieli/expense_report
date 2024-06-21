from abc import ABC
from pathlib import Path

import pandas as pd
import tabula
from loguru import logger
from pypdf import PdfReader
from ttp import ttp

from expense_report.data_extractors.common import Extractor
from expense_report.exceptions import SanityCheckError


class PDFExtractor(Extractor, ABC):

    def to_data_frame(self):
        logger.info(f"{self.bill_name}: extracting text from pdf")
        pdf_reader = PdfReader(self.pdf_file_path)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text() + "\n"

        logger.info(f"{self.bill_name}: extracting bill_sum")
        parser = ttp(data=pdf_text, template=self.bill_sum_ttp_template)
        parser.parse()
        ttp_parsed = parser.result()
        bill_sum = float(ttp_parsed[0][0]["bill_sum"].replace("'", ""))

        logger.info(f"{self.bill_name}: extracting tables from pdf")
        dfs_from_pdf = tabula.read_pdf(self.pdf_file_path, pages="all")

        # drop bonus table
        logger.info(f"{self.bill_name}: dropping table with bonus amounts")
        if self.drop_table_header_keyword in str(
            dfs_from_pdf[-1].columns.to_list()):
            del dfs_from_pdf[-1]

        logger.info(f"{self.bill_name}: preparing data")
        # concat
        df = pd.concat(dfs_from_pdf)

        # insert new column with filename
        df.insert(1, self.data_origin_column_name, self.bill_name)

        # convert to date
        df[self.date_column_name] = pd.to_datetime(
            df[self.date_column_name], format="%d.%m.%Y"
        )
        df = df.sort_values(by=self.date_column_name)

        # convert number columns
        number_columns = [self.charge_column_name, self.credit_column_name]
        for number_column in number_columns:
            df[number_column] = pd.to_numeric(
                df[number_column].astype(str).str.replace("'", ""),
                errors="coerce"
            )

        # filter lines to generate the sum
        logger.info(
            f"{self.bill_name}: remove lines {str(self.lines_to_remove)}")
        for line_to_remove in self.lines_to_remove:
            filter_df = df[
                self.transaction_description_column_name].str.contains(
                line_to_remove)
            df = df[~filter_df]

        charge_sum_value = df[self.charge_column_name].dropna().sum()
        if (charge_sum_value - bill_sum) < 1:
            logger.info(
                f"{self.bill_name}: sum {charge_sum_value} matches "
                f"expected value {bill_sum}"
            )
            return df
        else:
            error_msg = (
                f"Calculated sum '{charge_sum_value}' "
                f"does not match '{self.bill_sum_text}' {bill_sum}"
            )
            logger.error(f"{self.bill_name}: {error_msg}")
            raise SanityCheckError(error_msg)


class CembraBillPDFExtractor(PDFExtractor):
    date_column_name = "Einkaufs-Datum"
    charge_column_name = "Belastung CHF"
    credit_column_name = "Gutschrift CHF"
    transaction_description_column_name = "Beschreibung"
    data_origin_column_name = "Datenherkunft"
    bill_sum_text = "Neue Belastungen CHF"
    bill_sum_ttp_template = f"{bill_sum_text} {{{{ bill_sum }}}}"
    lines_to_remove = ["Ihre LSV-Zahlung - Besten Dank",
                       "Saldovortrag letzte Rechnung"]
    drop_table_header_keyword = "ckverg"

    def __init__(self, pdf_file_path: Path):
        self.pdf_file_path = pdf_file_path
        self.bill_name = self.pdf_file_path.name

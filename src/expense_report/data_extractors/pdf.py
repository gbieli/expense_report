from abc import ABC

import pandas as pd
import tabula
from loguru import logger
from pypdf import PdfReader
from ttp import ttp

from expense_report.data_extractors.base import ColumnNames, Extractor
from expense_report.exceptions import SanityCheckError


class PDFFileExtractor(Extractor, ABC):
    bill_sum_text: str
    bill_sum_ttp_template: str
    lines_to_remove: list
    drop_table_header_keyword: str

    def to_data_frame(self):
        pdf_text = self._pdf_extract_text()

        bill_sum = self._extract_bill_sum(pdf_text)

        dfs_from_pdf = self._extract_tables_from_pdf()

        # drop table matching header keyword
        logger.info(f"{self.file_name}: dropping table matching header keyword")
        if self.drop_table_header_keyword in str(dfs_from_pdf[-1].columns.to_list()):
            del dfs_from_pdf[-1]

        return self._prepare_data_frame(dfs_from_pdf, bill_sum)

    def _extract_tables_from_pdf(self):
        logger.info(f"{self.file_name}: extracting tables from pdf")
        dfs_from_pdf = tabula.read_pdf(self.file_path, pages="all")
        return dfs_from_pdf

    def _prepare_data_frame(self, dfs_from_pdf, bill_sum):
        logger.info(f"{self.file_name}: preparing data")
        # concat
        df = pd.concat(dfs_from_pdf)
        df = self._insert_convert(df, "%d.%m.%Y")
        # filter lines to generate the sum
        logger.info(f"{self.file_name}: remove lines {str(self.lines_to_remove)}")
        for line_to_remove in self.lines_to_remove:
            filter_df = df[self.column_names.transaction_description].str.contains(
                line_to_remove
            )
            df = df[~filter_df]
        charge_sum_value = df[self.column_names.charge].dropna().sum()
        if (charge_sum_value - bill_sum) < 1:
            logger.info(
                f"{self.file_name}: sum {charge_sum_value} matches "
                f"expected value {bill_sum}"
            )
            return df
        else:
            error_msg = (
                f"Calculated sum '{charge_sum_value}' "
                f"does not match '{self.bill_sum_text}' {bill_sum}"
            )
            logger.error(f"{self.file_name}: {error_msg}")
            raise SanityCheckError(error_msg)

    def _extract_bill_sum(self, pdf_text):
        logger.info(f"{self.file_name}: extracting bill_sum")
        parser = ttp(data=pdf_text, template=self.bill_sum_ttp_template)
        parser.parse()
        ttp_parsed = parser.result()
        bill_sum = float(ttp_parsed[0][0]["bill_sum"].replace("'", ""))
        return bill_sum

    def _pdf_extract_text(self):
        logger.info(f"{self.file_name}: extracting text from pdf")
        pdf_reader = PdfReader(self.file_path)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text() + "\n"
        return pdf_text


class CembraPDFFileExtractor(PDFFileExtractor):
    column_names = ColumnNames(
        shop_date="Einkaufs-Datum",
        charge="Belastung CHF",
        credit="Gutschrift CHF",
        transaction_description="Beschreibung",
        data_origin="Datenherkunft",
    )

    file_type = "pdf"
    bill_sum_text = "Neue Belastungen CHF"
    bill_sum_ttp_template = f"{bill_sum_text} {{{{ bill_sum }}}}"
    lines_to_remove = ["Ihre LSV-Zahlung - Besten Dank", "Saldovortrag letzte Rechnung"]
    drop_table_header_keyword = "ckverg"

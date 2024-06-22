from abc import ABC
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import tabula
from loguru import logger
from pypdf import PdfReader
from ttp import ttp

from expense_report.data_extractors.base import Extractor
from expense_report.data_extractors.common import beschreibung_category
from expense_report.exceptions import SanityCheckError


@dataclass
class ColumnNames:
    shop_date: str
    charge: str
    credit: str
    transaction_description: str
    data_origin: str


class PDFExtractor(Extractor, ABC):
    column_names: ColumnNames
    bill_sum_text: str
    bill_sum_ttp_template: str
    lines_to_remove: list
    drop_table_header_keyword: str

    def __init__(self, pdf_file_path: Path):
        self.pdf_file_path = pdf_file_path
        self.bill_name = self.pdf_file_path.name

    def to_data_frame(self):
        pdf_text = self.pdf_extract_text()

        bill_sum = self.extract_bill_sum(pdf_text)

        dfs_from_pdf = self.extract_tables_from_pdf()

        # drop table matching header keyword
        logger.info(f"{self.bill_name}: dropping table matching header keyword")
        if self.drop_table_header_keyword in str(dfs_from_pdf[-1].columns.to_list()):
            del dfs_from_pdf[-1]

        return self.prepare_data_frame(dfs_from_pdf, bill_sum)

    def extract_tables_from_pdf(self):
        logger.info(f"{self.bill_name}: extracting tables from pdf")
        dfs_from_pdf = tabula.read_pdf(self.pdf_file_path, pages="all")
        return dfs_from_pdf

    def prepare_data_frame(self, dfs_from_pdf, bill_sum):
        logger.info(f"{self.bill_name}: preparing data")
        # concat
        df = pd.concat(dfs_from_pdf)
        # insert new column with filename
        df.insert(1, self.column_names.data_origin, self.bill_name)
        # convert to date
        df[self.column_names.shop_date] = pd.to_datetime(
            df[self.column_names.shop_date], format="%d.%m.%Y"
        )
        df = df.sort_values(by=self.column_names.shop_date)
        # convert number columns
        number_columns = [self.column_names.charge, self.column_names.credit]
        for number_column in number_columns:
            df[number_column] = pd.to_numeric(
                df[number_column].astype(str).str.replace("'", ""), errors="coerce"
            )
        # filter lines to generate the sum
        logger.info(f"{self.bill_name}: remove lines {str(self.lines_to_remove)}")
        for line_to_remove in self.lines_to_remove:
            filter_df = df[self.column_names.transaction_description].str.contains(
                line_to_remove
            )
            df = df[~filter_df]
        charge_sum_value = df[self.column_names.charge].dropna().sum()
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

    def extract_bill_sum(self, pdf_text):
        logger.info(f"{self.bill_name}: extracting bill_sum")
        parser = ttp(data=pdf_text, template=self.bill_sum_ttp_template)
        parser.parse()
        ttp_parsed = parser.result()
        bill_sum = float(ttp_parsed[0][0]["bill_sum"].replace("'", ""))
        return bill_sum

    def pdf_extract_text(self):
        logger.info(f"{self.bill_name}: extracting text from pdf")
        pdf_reader = PdfReader(self.pdf_file_path)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text() + "\n"
        return pdf_text

    @staticmethod
    def pdfs_to_excel(pdf_files, excel_file_path: Path, sheet_name: str,
                      extractor_class: "PDFExtractor"):
        df_list = []
        for pdf_file_path in pdf_files:
            df_from_pdf = extractor_class(pdf_file_path).to_data_frame()
            df_list.append(df_from_pdf)
        df = pd.concat(df_list)
        df["Jahr"] = df["Einkaufs-Datum"].dt.year
        df["Kategorie"] = df["Beschreibung"].apply(beschreibung_category)
        df_pivot_beschreibung = df.pivot_table(values="Belastung CHF",
                                               index="Beschreibung",
                                               columns="Jahr", aggfunc="sum",
                                               fill_value=0.0)
        df_pivot_kategorie = df.pivot_table(values="Belastung CHF", index="Kategorie",
                                            columns="Jahr", aggfunc="sum",
                                            fill_value=0.0)
        logger.info(f"Resulting dataframe: {str(df)}")

        # Write dataframe to excel
        logger.info(f"Generating Excel file at '{excel_file_path}'")
        with pd.ExcelWriter(excel_file_path) as writer:
            df.to_excel(writer, sheet_name=sheet_name)
            df_pivot_beschreibung.to_excel(writer, sheet_name="pivot_beschreibung")
            df_pivot_kategorie.to_excel(writer, sheet_name="pivot_kategorie")


class CembraBillPDFExtractor(PDFExtractor):
    column_names = ColumnNames(
        shop_date="Einkaufs-Datum",
        charge="Belastung CHF",
        credit="Gutschrift CHF",
        transaction_description="Beschreibung",
        data_origin="Datenherkunft",
    )

    bill_sum_text = "Neue Belastungen CHF"
    bill_sum_ttp_template = f"{bill_sum_text} {{{{ bill_sum }}}}"
    lines_to_remove = ["Ihre LSV-Zahlung - Besten Dank", "Saldovortrag letzte Rechnung"]
    drop_table_header_keyword = "ckverg"

from pathlib import Path, PosixPath

import pandas as pd
import tabula
from loguru import logger
from pypdf import PdfReader
from ttp import ttp

from expense_report.private import paths_pdfs


def pdfs_to_excel(pdf_files, excel_file_path, sheet_name):
    df_list = []
    for pdf_file_path in pdf_files:
        df_from_pdf = pdf_to_data_frames(pdf_file_path)
        df_list.append(df_from_pdf)
    df_concat = pd.concat(df_list)
    logger.info(f"Resulting dataframe: {str(df_concat)}")

    # Write dataframe to excel
    logger.info(f"Generating Excel file at '{excel_file_path}'")
    with pd.ExcelWriter(excel_file_path) as writer:
        df_concat.to_excel(writer, sheet_name=sheet_name)


class SanityCheckError(Exception):
    pass


def pdf_to_data_frames(pdf_file_path: PosixPath):
    bill_name = pdf_file_path.name
    date_column_name = "Einkaufs-Datum"
    charge_column_name = "Belastung CHF"
    credit_column_name = "Gutschrift CHF"

    logger.info(f"{bill_name}: extracting text from pdf")
    pdf_reader = PdfReader(pdf_file_path)
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text() + "\n"

    logger.info(f"{bill_name}: extracting bill_sum")
    ttp_template = "Neue Belastungen CHF {{ bill_sum }}"
    parser = ttp(data=pdf_text, template=ttp_template)
    parser.parse()
    ttp_parsed = parser.result()
    bill_sum = float(ttp_parsed[0][0]["bill_sum"].replace("'", ""))

    logger.info(f"{bill_name}: extracting tables from pdf")
    dfs_from_pdf = tabula.read_pdf(pdf_file_path, pages="all")

    # drop bonus table
    logger.info(f"{bill_name}: dropping table with bonus amounts")
    if "ckverg" in str(dfs_from_pdf[-1].columns.to_list()):
        del dfs_from_pdf[-1]

    logger.info(f"{bill_name}: preparing data")
    # concat
    df = pd.concat(dfs_from_pdf)

    # insert new column with filename
    df.insert(1, "Rechnung", bill_name)

    # convert to date
    df[date_column_name] = pd.to_datetime(df[date_column_name],
                                          format="%d.%m.%Y")
    df = df.sort_values(by=date_column_name)

    # convert number columns
    number_columns = [charge_column_name, credit_column_name]
    for number_column in number_columns:
        df[number_column] = pd.to_numeric(
            df[number_column].astype(str).str.replace("'", ""),
            errors="coerce"
        )

    # filter lines to generate the sum
    to_remove = ["Ihre LSV-Zahlung - Besten Dank",
                 "Saldovortrag letzte Rechnung"]
    logger.info(f"{bill_name}: remove lines {str(to_remove)}")
    for line_to_remove in to_remove:
        filter_df = df["Beschreibung"].str.contains(line_to_remove)
        df = df[~filter_df]

    sum_value = df[charge_column_name].dropna().sum()
    if sum_value - bill_sum < 1:
        logger.info(
            f"{bill_name}: sum {sum_value} matches expected value {bill_sum}")
        return df
    else:
        error_msg = (
            f"Calculated sum '{sum_value}' "
            f"does not match 'Neue Belastungen CHF' {bill_sum}"
        )
        logger.error(f"{bill_name}: {error_msg}")
        raise SanityCheckError(error_msg)


def main():
    logger.info("Start")
    for account, path in paths_pdfs.items():
        p = Path(path)
        files = list(p.glob("*.pdf"))
        pdfs_to_excel(files, p / f"{account}_combined.xlsx", account)
    logger.info("End")


if __name__ == "__main__":
    main()

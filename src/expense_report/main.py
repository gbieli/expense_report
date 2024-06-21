from pathlib import Path

import pandas as pd
from loguru import logger

from expense_report.data_extractors.pdf import CembraBillPDFExtractor
from expense_report.private import paths_pdfs


def pdfs_to_excel(pdf_files, excel_file_path: Path, sheet_name):
    df_list = []
    for pdf_file_path in pdf_files:
        df_from_pdf = CembraBillPDFExtractor(pdf_file_path).to_data_frame()
        df_list.append(df_from_pdf)
    df_concat = pd.concat(df_list)
    logger.info(f"Resulting dataframe: {str(df_concat)}")

    # Write dataframe to excel
    logger.info(f"Generating Excel file at '{excel_file_path}'")
    with pd.ExcelWriter(excel_file_path) as writer:
        df_concat.to_excel(writer, sheet_name=sheet_name)


def main():
    logger.info("Start")
    for account, path in paths_pdfs.items():
        p = Path(path)
        files = list(p.glob("*.pdf"))
        pdfs_to_excel(files, p / f"{account}_combined.xlsx", account)
    logger.info("End")


if __name__ == "__main__":
    main()

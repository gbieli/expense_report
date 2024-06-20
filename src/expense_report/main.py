from pathlib import Path

import pandas as pd
import tabula

from expense_report.private import paths_pdfs


def pdf_to_excel(pdf_file_path, excel_file_path):
    # Read PDF file
    tables = tabula.read_pdf(pdf_file_path, pages="all")

    # Write each table to a separate sheet in the Excel file
    with pd.ExcelWriter(excel_file_path) as writer:
        for i, table in enumerate(tables):
            table.to_excel(writer, sheet_name=f"Sheet{i+1}")


def main():
    for account, path in paths_pdfs.items():
        p = Path(path)
        files = list(p.glob("*.pdf"))
        for file in files:
            pdf_to_excel(file, file.with_suffix(".xlsx"))


if __name__ == "__main__":
    main()

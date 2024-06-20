import tabula
import pandas as pd
from pathlib import Path

from expense_report.private import paths


def pdf_to_excel(pdf_file_path, excel_file_path):
    # Read PDF file
    tables = tabula.read_pdf(pdf_file_path, pages='all')

    # Write each table to a separate sheet in the Excel file
    with pd.ExcelWriter(excel_file_path) as writer:
        for i, table in enumerate(tables):
            table.to_excel(writer, sheet_name=f'Sheet{i+1}')


if __name__ == "__main__":
    for account, path in paths.items():
        p = Path(path)
        files = list(p.glob("*.pdf"))
        for file in files:
            pdf_to_excel(file, file.with_suffix(".xlsx"))

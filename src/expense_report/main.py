from pathlib import Path

import pandas as pd
import tabula

from expense_report.private import paths_pdfs


def pdfs_to_excel(pdf_files, excel_file_path, sheet_name):
    # Read PDF file
    df_list = []
    for pdf_file_path in pdf_files:
        dfs_from_pdf = tabula.read_pdf(pdf_file_path, pages="all")
        if "ckverg" in str(dfs_from_pdf[-1].columns.to_list()):
            del dfs_from_pdf[-1]
        df_list.extend(dfs_from_pdf)
    df_concat = pd.concat(df_list)
    print(df_concat)
    # Write each table to a separate sheet in the Excel file
    with pd.ExcelWriter(excel_file_path) as writer:
        df_concat.to_excel(writer, sheet_name=sheet_name)


def main():
    for account, path in paths_pdfs.items():
        p = Path(path)
        files = list(p.glob("*.pdf"))
        pdfs_to_excel(files, p / f"{account}_combined.xlsx", account)


if __name__ == "__main__":
    main()

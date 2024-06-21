from pathlib import Path, PosixPath

import pandas as pd
import tabula

from expense_report.private import paths_pdfs

from pypdf import PdfReader


def pdfs_to_excel(pdf_files, excel_file_path, sheet_name):
    df_list = []
    for pdf_file_path in pdf_files:
        df_from_pdf = pdf_to_data_frames(pdf_file_path)
        df_list.append(df_from_pdf)
    df_concat = pd.concat(df_list)
    print(df_concat)
    # Write each table to a separate sheet in the Excel file
    with pd.ExcelWriter(excel_file_path) as writer:
        df_concat.to_excel(writer, sheet_name=sheet_name)


def pdf_to_data_frames(pdf_file_path: PosixPath):
    bill_name = pdf_file_path.name

    reader = PdfReader(pdf_file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    bill_sum = ""
    for line in text.splitlines():
        if "Neue Belastungen CHF" in line:
            bill_sum_line = line
    dfs_from_pdf = tabula.read_pdf(pdf_file_path, pages="all")
    if "ckverg" in str(dfs_from_pdf[-1].columns.to_list()):
        del dfs_from_pdf[-1]
    df_concatted = pd.concat(dfs_from_pdf)
    df_concatted.insert(1, "Rechnung", bill_name)
    date_column_name = "Einkaufs-Datum"
    df_concatted[date_column_name] = pd.to_datetime(
        df_concatted[date_column_name])
    df_sorted = df_concatted.sort_values(by=date_column_name)
    return df_sorted


def main():
    for account, path in paths_pdfs.items():
        p = Path(path)
        files = list(p.glob("*.pdf"))
        pdfs_to_excel(files, p / f"{account}_combined.xlsx", account)


if __name__ == "__main__":
    main()

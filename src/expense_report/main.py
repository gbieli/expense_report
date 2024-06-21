from pathlib import Path, PosixPath

import pandas as pd
import tabula

from expense_report.private import paths_pdfs

from pypdf import PdfReader
from ttp import ttp


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
    pdf_reader = PdfReader(pdf_file_path)
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text() + "\n"
    ttp_template = "Neue Belastungen CHF {{ bill_sum }}"
    parser = ttp(data=pdf_text, template=ttp_template)
    parser.parse()
    ttp_parsed = parser.result()
    bill_sum = float(ttp_parsed[0][0]["bill_sum"].replace("'", ""))
    dfs_from_pdf = tabula.read_pdf(pdf_file_path, pages="all")
    if "ckverg" in str(dfs_from_pdf[-1].columns.to_list()):
        del dfs_from_pdf[-1]
    df_concatted = pd.concat(dfs_from_pdf)
    df_concatted.insert(1, "Rechnung", bill_name)
    date_column_name = "Einkaufs-Datum"
    df_concatted[date_column_name] = pd.to_datetime(
        df_concatted[date_column_name])
    df_sorted = df_concatted.sort_values(by=date_column_name).astype(str)
    charge_column_name = "Belastung CHF"
    credit_column_name = "Gutschrift CHF"
    df_sorted[charge_column_name] = pd.to_numeric(
        df_sorted[charge_column_name].str.replace("'", ""), errors="coerce")
    df_sorted[credit_column_name] = pd.to_numeric(
        df_sorted[credit_column_name].str.replace("'", ""), errors="coerce")
    if df_sorted[charge_column_name].dropna().sum() - df_sorted[
        credit_column_name].dropna().sum() == bill_sum:
        pass
    return df_sorted


def main():
    for account, path in paths_pdfs.items():
        p = Path(path)
        files = list(p.glob("*.pdf"))
        pdfs_to_excel(files, p / f"{account}_combined.xlsx", account)


if __name__ == "__main__":
    main()

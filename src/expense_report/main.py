from pathlib import Path

import pandas as pd
from loguru import logger

from expense_report.data_extractors.pdf import CembraBillPDFExtractor
from expense_report.private import paths_pdfs, categories_and_keywords


def pdfs_to_excel(pdf_files, excel_file_path: Path, sheet_name):
    df_list = []
    for pdf_file_path in pdf_files:
        df_from_pdf = CembraBillPDFExtractor(pdf_file_path).to_data_frame()
        df_list.append(df_from_pdf)
    df = pd.concat(df_list)
    df["Jahr"] = df["Einkaufs-Datum"].dt.year
    df["Kategorie"] = df["Beschreibung"].apply(beschreibung_category)
    df_pivot_beschreibung = df.pivot_table(values="Belastung CHF", index="Beschreibung",
                       columns="Jahr", aggfunc="sum", fill_value=0.0)
    df_pivot_kategorie = df.pivot_table(values="Belastung CHF", index="Kategorie",
                       columns="Jahr", aggfunc="sum", fill_value=0.0)
    logger.info(f"Resulting dataframe: {str(df)}")

    # Write dataframe to excel
    logger.info(f"Generating Excel file at '{excel_file_path}'")
    with pd.ExcelWriter(excel_file_path) as writer:
        df.to_excel(writer, sheet_name=sheet_name)
        df_pivot_beschreibung.to_excel(writer, sheet_name="pivot_beschreibung")
        df_pivot_kategorie.to_excel(writer, sheet_name="pivot_kategorie")


def beschreibung_category(beschreibung):
    for keyword, category in categories_and_keywords_by_keyword().items():
        if keyword in beschreibung.lower():
            return category
    return "unkategorisiert"


def categories_and_keywords_by_keyword():
    keywords_and_categories = {}
    for category, keywords in categories_and_keywords.items():
        for keyword in keywords:
            keywords_and_categories[keyword] = category

    return keywords_and_categories


def main():
    logger.info("Start")
    for account, path in paths_pdfs.items():
        p = Path(path)
        files = list(p.glob("*.pdf"))
        pdfs_to_excel(files, p / f"{account}_combined.xlsx", account)
    logger.info("End")


if __name__ == "__main__":
    main()

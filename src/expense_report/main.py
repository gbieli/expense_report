from pathlib import Path

from loguru import logger

from expense_report.data_extractors.pdf import PDFExtractor, CembraBillPDFExtractor
from expense_report.private import paths_account_files


def main():
    logger.info("Start")
    for account_type, path in paths_account_files.items():
        p = Path(path)
        files = list(p.glob("*.pdf"))
        PDFExtractor.pdfs_to_excel(files, p / f"{account_type}_combined.xlsx",
                                   account_type, CembraBillPDFExtractor)
    logger.info("End")


if __name__ == "__main__":
    main()

from pathlib import Path

from loguru import logger

from expense_report.account import CembraAccount
from expense_report.private import paths_account_files


def main():
    logger.info("Start")
    for account_type, path in paths_account_files.items():
        # todo: make account type selection generic
        p = Path(path)
        a = CembraAccount(
            "hk_cembra", list(p.glob("*.pdf")), p / f"{account_type}_combined.xlsx"
        )
        a.generate_excel()

    logger.info("End")


if __name__ == "__main__":
    main()

from pathlib import Path

from loguru import logger

from expense_report.account import Account
from expense_report.private import paths_account_files


def main():
    logger.info("Start")
    for account_type, path in paths_account_files.items():
        p = Path(path)
        a = Account.get_account_instance(
            account_type,
            "hk_cembra",
            p,
            p / f"{account_type}_combined.xlsx",
        )
        a.generate_excel()

    logger.info("End")


if __name__ == "__main__":
    main()

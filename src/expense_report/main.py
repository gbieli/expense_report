from pathlib import Path

from loguru import logger

from expense_report.account import Account
from expense_report.private_settings import paths_account_files


def main():
    logger.info("Start")
    for account_name, params in paths_account_files.items():
        p = Path(params["path"])
        a = Account.get_account_instance(
            params["account_type"],
            account_name,
            p,
            p / f"{params["account_type"]}_combined.xlsx",
        )
        a.generate_excel()

    logger.info("End")


if __name__ == "__main__":
    main()

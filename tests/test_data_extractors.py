from pathlib import Path

import pytest

from expense_report.account import Account
from expense_report.enums import AccountType

output_folder = Path("tests/outputs")


@pytest.mark.parametrize(
    argnames=["path_to_pdf_inputs_folder", "account_type", "account_id"],
    argvalues=[
        (Path("tests/test_data/cembra"), AccountType.cembra, "cembra_kk"),
        (Path("tests/test_data/post"), AccountType.post_finance, "post_hk"),
        (Path("tests/test_data/neon"), AccountType.neon, "neon_private"),
    ],
    ids=["cembra", "post", "neon"]
)
def test_extractor(path_to_pdf_inputs_folder, account_type, account_id):
    a = Account.get_account_instance(
        account_type,
        account_id,
        path_to_pdf_inputs_folder,
        output_folder / f"{account_type.name}_combined.xlsx",
    )
    a.generate_excel()

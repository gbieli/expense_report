from enum import Enum

from expense_report.data_extractors.pdf import CembraBillPDFExtractor


class AccountTypes(Enum):
    cembra: CembraBillPDFExtractor

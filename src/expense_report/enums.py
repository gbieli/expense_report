from enum import Enum

from expense_report.data_extractors.csv import (NeonCSVFileExtractor,
                                                PostFinanceCSVFileExtractor)
from expense_report.data_extractors.pdf import CembraPDFFileExtractor


class AccountType(Enum):
    cembra = CembraPDFFileExtractor
    neon = NeonCSVFileExtractor
    post_finance = PostFinanceCSVFileExtractor

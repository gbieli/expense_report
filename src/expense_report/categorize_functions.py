from expense_report.config import Config


def beschreibung_category(beschreibung):
    """
    Used in pandas df apply function to categorize expense.
    :param beschreibung: pandas "Beschreibung" field
    :return:
    """
    for keyword, category in categories_and_keywords_by_keyword().items():
        if keyword in beschreibung.lower():
            return category
    return "unkategorisiert"


def categories_and_keywords_by_keyword():
    """
    Invert the data categories structure.
    :return:
    """
    keywords_and_categories = {}
    for category, keywords in Config.get_categories_and_keywords().items():
        for keyword in keywords:
            keywords_and_categories[keyword] = category

    return keywords_and_categories

from expense_report.config import Config


def test_config():
    Config.set_config_path("")
    Config.get_categories_and_keywords()
    Config.get_paths_account_files()

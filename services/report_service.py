# This file will later talk to SQLite
# For now, it returns REALISTIC structured data

def get_expenses_by_category():
    """
    Returns a list of (category_name, total_amount)
    """
    return [
        ("Τρόφιμα", 320),
        ("Ενοίκιο", 600),
        ("Μεταφορές", 180)
    ]


def get_monthly_summary():
    """
    Returns a dict with income/expense per month
    """
    return {
        "Ιανουάριος": {"income": 1200, "expense": 900},
        "Φεβρουάριος": {"income": 1400, "expense": 1000}
    }

"""Στατιστικά για ta reports και τα γραφήματα"""
from datetime import date

from backend.exceptions import ValidationError
from backend.repositories import TransactionRepository


class StatsService:
    """Υπολογισμοί ισοζυγίου κατανομής και σύγκρισης μηνών"""

    def __init__(self, database):
        self.repo = TransactionRepository(database)

    # ---- Validators ----

    def validate_month(self, month):
        if month is None:
            return None
        try:
            month = int(month)
        except (TypeError, ValueError):
            raise ValidationError("Ο μήνας πρέπει να είναι αριθμός.")
        if month < 1 or month > 12:
            raise ValidationError("Ο μήνας πρέπει να είναι 1-12.")
        return month

    def validate_year(self, year):
        if year is None:
            return None
        try:
            year = int(year)
        except (TypeError, ValueError):
            raise ValidationError("Το έτος πρέπει να είναι αριθμός.")
        if year < 1900 or year > 2100:
            raise ValidationError("Μη έγκυρο έτος.")
        return year


    def get_balance(self, year=None, month=None):
        """
        Υπολογισμός του ισοζυγιου.
        Επιστρέφει: {"income": X, "expense": Y, "balance": X-Y}
        """
        year = self.validate_year(year)
        month = self.validate_month(month)

        total_income = self.repo.sum_by_type("income", year=year, month=month)
        total_expense = self.repo.sum_by_type("expense", year=year, month=month)

        return {
            "income": round(total_income, 2),
            "expense": round(total_expense, 2),
            "balance": round(total_income - total_expense, 2),
        }

    def get_category_distribution(self, txn_type, year=None, month=None):
        """
        Κατανομή συναλλαγών ανά κατηγορία (για pie chart).
        Επιστρέφει: [{category_name, total, percentage, ...}, ...]
        """
        if txn_type not in ("income", "expense"):
            raise ValidationError(f"Μη έγκυρος τύπος: '{txn_type}'")
        year = self.validate_year(year)
        month = self.validate_month(month)

        rows = self.repo.sum_by_category(txn_type=txn_type, year=year, month=month)
        grand_total = sum(row["total"] for row in rows)

        result = []
        for row in rows:
            if grand_total > 0:
                percentage = (row["total"] / grand_total) * 100
            else:
                percentage = 0.0
            result.append({
                "category_id": row["category_id"],
                "category_name": row["category_name"],
                "total": round(row["total"], 2),
                "percentage": round(percentage, 2),
            })
        return result

    def compare_months(self, months_back=6, reference_date=None):
        """
        Σύγκριση εσόδων/εξόδων/ισοζυγίου για τους τελευταίους Ν μήνες για bar chart
        Επιστρέφει λίστα από παλαιότερο προς νεότερο
        """
        if months_back < 1 or months_back > 36:
            raise ValidationError("months_back πρέπει να είναι 1-36.")

        if reference_date is None:
            reference_date = date.today()

        # Υπολογισμός περιόδων παλαιότερος προς νεότερο
        periods = []
        y, m = reference_date.year, reference_date.month
        for _ in range(months_back):
            periods.append((y, m))
            m -= 1
            if m == 0:
                m = 12
                y -= 1
        periods.reverse()

        result = []
        for year, month in periods:
            balance_data = self.get_balance(year=year, month=month)
            result.append({
                "year": year,
                "month": month,
                "label": f"{year:04d}-{month:02d}",
                "income": balance_data["income"],
                "expense": balance_data["expense"],
                "balance": balance_data["balance"],
            })
        return result

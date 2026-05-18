"""Παρακολούθηση του budget ανά κατηγορία"""
from datetime import date

from backend.exceptions import NotFoundError
from backend.repositories import CategoryRepository, TransactionRepository


# Όρια για τα warnings σε ποσοστά
WARNING_THRESHOLD = 80.0   # >= 80% ειδοποίηση οτι πλησιάζει
DANGER_THRESHOLD = 100.0   # >= 100% ξεπεράστηκε


class BudgetService:
    """Παρακολούθηση ορίων δαπανών ανά κατηγορία"""

    def __init__(self, database):
        self.cat_repo = CategoryRepository(database)
        self.txn_repo = TransactionRepository(database)

    def check_category_budget(self, category_id, year=None, month=None):
        """
        Ελέγχει το budget μιας κατηγορίας για συγκεκριμένο μήνα.
        Status: 'ok' | 'warning' | 'exceeded' | 'no_budget'
        """
        # Default είναι ο μήνας που είμαστε
        if year is None and month is None:
            today = date.today()
            year = today.year
            month = today.month

        category = self.cat_repo.get_by_id(category_id)
        if category is None:
            raise NotFoundError(f"Δεν βρέθηκε κατηγορία με id={category_id}")

        spent = self.get_spent_for_category(category_id, year, month)

        # Δεν έχει οριστεί budget
        if category.monthly_budget is None:
            return {
                "category_id": category.id,
                "category_name": category.name,
                "budget": None,
                "spent": round(spent, 2),
                "remaining": None,
                "percentage": None,
                "status": "no_budget",
            }

        budget = category.monthly_budget
        if budget == 0:
            percentage = 100.0 if spent > 0 else 0.0
        else:
            percentage = (spent / budget) * 100

        if percentage >= DANGER_THRESHOLD:
            status = "exceeded"
        elif percentage >= WARNING_THRESHOLD:
            status = "warning"
        else:
            status = "ok"

        return {
            "category_id": category.id,
            "category_name": category.name,
            "budget": round(budget, 2),
            "spent": round(spent, 2),
            "remaining": round(budget - spent, 2),
            "percentage": round(percentage, 2),
            "status": status,
        }

    def get_all_budget_statuses(self, year=None, month=None, only_with_budget=True):
        """Λίστα με status για όλες τις expense κατηγορίες"""
        categories = self.cat_repo.get_all(active_only=True, type_filter="expense")
        result = []
        for cat in categories:
            if only_with_budget and cat.monthly_budget is None:
                continue
            status = self.check_category_budget(cat.id, year=year, month=month)
            result.append(status)

        # Ταξινόμηση: exceeded → warning → ok → no_budget
        # Φτιάχνουμε ξεχωριστές λίστες ανάλογα με το status
        exceeded_list = []
        warning_list = []
        ok_list = []
        no_budget_list = []

        for item in result:
            if item["status"] == "exceeded":
                exceeded_list.append(item)
            elif item["status"] == "warning":
                warning_list.append(item)
            elif item["status"] == "ok":
                ok_list.append(item)
            else:
                no_budget_list.append(item)

        # Τις ενώνουμε με τη σωστή σειρά
        return exceeded_list + warning_list + ok_list + no_budget_list

    def get_warnings(self, year=None, month=None):
        """Μόνο κατηγορίες σε warning ή exceeded κατάσταση"""
        all_statuses = self.get_all_budget_statuses(
            year=year, month=month, only_with_budget=True,
        )
        return [s for s in all_statuses if s["status"] in ("warning", "exceeded")]

    def get_spent_for_category(self, category_id, year, month):
        """Πόσα έχουν ξοδευτεί σε αυτή την κατηγορία τον μήνα"""
        rows = self.txn_repo.sum_by_category(
            txn_type="expense", year=year, month=month,
        )
        for row in rows:
            if row["category_id"] == category_id:
                return row["total"]
        return 0.0

"""Business logic για συναλλαγές εσόδων και εξόδων"""
from datetime import datetime, date

from backend.exceptions import NotFoundError, ValidationError
from backend.models import Transaction
from backend.repositories import (
    CategoryRepository,
    TransactionRepository,
)


VALID_TXN_TYPES = ("income", "expense")


class TransactionService:
    """Διαχείριση εσόδων/εξόδων με validation"""

    def __init__(self, database):
        self.repo = TransactionRepository(database)
        self.cat_repo = CategoryRepository(database)

    def validate_amount(self, amount):
        if amount is None:
            raise ValidationError("Το ποσό είναι υποχρεωτικό.")
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise ValidationError("Το ποσό πρέπει να είναι αριθμός.")
        if amount <= 0:
            raise ValidationError("Το ποσό πρέπει να είναι θετικό.")
        return round(amount, 2)

    def validate_txn_type(self, txn_type):
        if txn_type not in VALID_TXN_TYPES:
            raise ValidationError(
                f"Μη έγκυρος τύπος συναλλαγής: '{txn_type}'. "
                f"Αποδεκτές τιμές: {VALID_TXN_TYPES}"
            )
        return txn_type

    def validate_date(self, txn_date):
        """
        Δέχεται string DD-MM-YYYY
        Επιστρέφει string DD-MM-YYYY
        """
        if txn_date is None:
            raise ValidationError("Η ημερομηνία είναι υποχρεωτική.")
        if isinstance(txn_date, date):
            return txn_date.strftime("%Y-%m-%d")
        if isinstance(txn_date, str):
            try:
                # validate format
                datetime.strptime(txn_date, "%Y-%m-%d")
                return txn_date
            except ValueError:
                raise ValidationError(
                    f"Μη έγκυρη ημερομηνία: {txn_date}. Χρησιμοποίησε YYYY-MM-DD"
                )
        raise ValidationError("Μη έγκυρος ημερομηνία")

    def validate_category(self, category_id, txn_type):
        """
        Ελέγχει αν υπάρχει η κατηγορία και αν ταιριάζει με τον τύπο συναλλαγής.
        """
        if category_id is None:
            return None
        category = self.cat_repo.get_by_id(category_id)
        if category is None:
            raise ValidationError(
                f"Δεν υπάρχει κατηγορία με id={category_id}"
            )
        if not category.is_active:
            raise ValidationError(
                f"Η κατηγορία {category.name} είναι ανενεργή."
            )
        # Έλεγχος συμβατότητας τύπου
        if category.type != "both" and category.type != txn_type:
            raise ValidationError(
                f"Η κατηγορία {category.name} δεν επιτρέπεται για {'έσοδα' if txn_type == 'income' else 'έξοδα'}.")
        return category_id

    def add_income(self, amount, category_id=None, txn_date=None, note=None):
        """Συντομεση για εισαγωγή εσόδου"""
        return self.create_transaction(
            "income", amount, category_id, txn_date, note
        )

    def add_expense(self, amount, category_id=None, txn_date=None, note=None):
        """Συντομεύση για εισαγωγή εξόδου."""
        return self.create_transaction(
            "expense", amount, category_id, txn_date, note
        )

    def create_transaction(self, txn_type, amount, category_id, txn_date, note):
        """ Ίδια λογική για add_income και add_expense"""
        txn_type = self.validate_txn_type(txn_type)
        amount = self.validate_amount(amount)
        # Αν δεν δοθεί date παίρνουμε τη σημερινή ημερομηνία!
        if txn_date is None:
            txn_date = date.today()
        txn_date = self.validate_date(txn_date)
        category_id = self.validate_category(category_id, txn_type)

        if note is not None:
            note = str(note).strip() or None

        txn = Transaction(
            txn_type=txn_type,
            amount=amount,
            txn_date=txn_date,
            category_id=category_id,
            note=note,
        )
        new_id = self.repo.create(txn)
        txn.id = new_id
        # Ξαναπαίρνουμε με category_name
        return self.repo.get_by_id(new_id)

    def get_transaction(self, txn_id):
        """Επιστρέφει Transaction και πετάει NotFoundError αν δεν υπάρχει"""
        txn = self.repo.get_by_id(txn_id)
        if txn is None:
            raise NotFoundError(
                f"Δεν βρέθηκε συναλλαγή με id={txn_id}"
            )
        return txn

    def update_transaction(self, txn_id, amount=None, category_id=None,
                           txn_date=None, note=None, txn_type=None):
        """Μερικό update της συναλλαγής"""
        txn = self.get_transaction(txn_id)

        if txn_type is not None:
            txn.txn_type = self.validate_txn_type(txn_type)
        if amount is not None:
            txn.amount = self.validate_amount(amount)
        if txn_date is not None:
            txn.txn_date = self.validate_date(txn_date)
        if category_id is not None:
            txn.category_id = self.validate_category(category_id, txn.txn_type)
        if note is not None:
            txn.note = str(note).strip() or None

        self.repo.update(txn)
        return self.repo.get_by_id(txn_id)

    def clear_category(self, txn_id):
        """Αφαιρεί την κατηγορία από τη συναλλαγή"""
        txn = self.get_transaction(txn_id)
        txn.category_id = None
        self.repo.update(txn)
        return self.repo.get_by_id(txn_id)

    def delete_transaction(self, txn_id):
        """Διαγραφή και πετάει NotFoundError αν δεν υπάρχει"""
        self.get_transaction(txn_id)  # επιβεβαίωση ύπαρξης
        self.repo.delete(txn_id)

    def list_transactions(self, txn_type=None, category_id=None,
                          year=None, month=None,
                          start_date=None, end_date=None,
                          limit=None):
        """Φιλτραρισμένη λίστα συναλλαγών"""
        if txn_type is not None:
            self.validate_txn_type(txn_type)
        if start_date is not None:
            start_date = self.validate_date(start_date)
        if end_date is not None:
            end_date = self.validate_date(end_date)

        return self.repo.list_transactions(
            txn_type=txn_type,
            category_id=category_id,
            year=year,
            month=month,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

"""Business logic για κατηγορίες."""
import sqlite3

from backend.exceptions import (
    NotFoundError,
    ValidationError,
    DuplicateError,
)
from backend.models import Category
from backend.repositories import CategoryRepository

# Επιτρεπόμενες τιμές για το πεδίο type
VALID_CATEGORY_TYPES = ("income", "expense", "both")


class CategoryService:
    """Διαχείριση κατηγοριών με validation"""

    def __init__(self, database):
        self.repo = CategoryRepository(database)

    def validate_name(self, name):
        if name is None:
            raise ValidationError("Το όνομα κατηγορίας είναι υποχρεωτικό.")
        name = name.strip()
        if name == "":
            raise ValidationError("Το όνομα κατηγορίας δεν μπορεί να είναι κενό.")
        if len(name) > 50:
            raise ValidationError("Το όνομα κατηγορίας είναι πολύ μεγάλο (max 50).")
        return name

    def validate_type(self, type_value):
        if type_value not in VALID_CATEGORY_TYPES:
            raise ValidationError(
                f"Μη έγκυρος τύπος κατηγορίας: '{type_value}' "
                f"Αποδεκτές τιμές: {VALID_CATEGORY_TYPES}"
            )
        return type_value

    def validate_budget(self, budget):
        if budget is None:
            return None
        try:
            budget = float(budget)
        except (TypeError, ValueError):
            raise ValidationError("Το budget πρέπει να είναι αριθμός.")
        if budget < 0:
            raise ValidationError("Το budget δεν μπορεί να είναι αρνητικό.")
        return budget

    def create_category(self, name, type, monthly_budget=None):
        """
        Δημιουργεί νέα κατηγορία και επιστρέφει το Category
        θα δώσει ValidationError αν τα data δεν είναι έγκυρα
        Θα δώσει DuplicateError αν υπάρχει ήδη κατηγορία με το ίδιο όνομα
        """
        name = self.validate_name(name)
        type = self.validate_type(type)
        monthly_budget = self.validate_budget(monthly_budget)

        category = Category(
            name=name,
            type=type,
            monthly_budget=monthly_budget,
            is_active=True,
        )
        try:
            new_id = self.repo.create(category)
        except sqlite3.IntegrityError:
            # Δεν μπορει να υπαρχει κατηγορία με ίδιο όνομα
            raise DuplicateError(
                f"Υπάρχει ήδη κατηγορία με όνομα {name}."
            )
        category.id = new_id
        return category

    def get_category(self, category_id):
        """Επιστρέφει Category και πετάει NotFoundError αν δεν υπάρχει."""
        category = self.repo.get_by_id(category_id)
        if category is None:
            raise NotFoundError(
                f"Δεν βρέθηκε κατηγορία με id={category_id}")
        return category

    def get_all_categories(self, active_only=True, type_filter=None):
        """Λίστα από Category objects"""
        if type_filter is not None:
            self.validate_type(type_filter)
        return self.repo.get_all(
            active_only=active_only,
            type_filter=type_filter,
        )

    def update_category(self, category_id, name=None, type=None,
                        monthly_budget=None, is_active=None):
        """
        Ενημερώνει μία κατηγορία αλλάζει μόνο τα πεδία που δίνονται και
        επιστρέφει το updated Category
        """
        category = self.get_category(category_id)

        if name is not None:
            category.name = self.validate_name(name)
        if type is not None:
            category.type = self.validate_type(type)
        if monthly_budget is not None:
            category.monthly_budget = self.validate_budget(monthly_budget)
        if is_active is not None:
            category.is_active = bool(is_active)

        try:
            self.repo.update(category)
        except sqlite3.IntegrityError:
            raise DuplicateError(
                f"Υπάρχει ήδη κατηγορία με όνομα {category.name}."
            )
        return category

    def set_budget(self, category_id, monthly_budget):
        """Ορίζει monthly_budget None για αφαίρεση"""
        return self.update_category(
            category_id,
            monthly_budget=monthly_budget,
        )

    def delete_category(self, category_id, hard=False):
        """
        Διαγραφή της κατηγορίας
        hard=False (default): soft delete (is_active=0).
        hard=True: μόνιμη διαγραφή. Οι συναλλαγές της κατηγορίας θα έχουν category_id=NULL
        """
        # επιβεβαίωση ύπαρξης και θα δώσει NotFoundError αν δεν υπάρχει
        self.get_category(category_id)

        if hard:
            self.repo.hard_delete(category_id)
        else:
            self.repo.soft_delete(category_id)

    def restore_category(self, category_id):
        """Επαναφέρει soft-deleted κατηγορία"""
        return self.update_category(category_id, is_active=True)

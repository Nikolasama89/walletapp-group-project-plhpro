"""Repository για τον πίνακα categories."""
from backend.models import Category


class CategoryRepository:
    """Create, Update, Read, Delete operations για τις κατηγορίες."""

    def __init__(self, database):
        self.db = database

    def row_to_category(self, row):
        """Μετατρέπει ένα sqlite3.Row σε Category object"""
        if row is None:
            return None
        return Category(
            id=row["id"],
            name=row["name"],
            type=row["type"],
            monthly_budget=row["monthly_budget"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, category):
        """Εισάγει νέα κατηγορία και επιστρέφει το id της"""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO categories (name, type, monthly_budget, is_active)
                VALUES (?, ?, ?, ?)
                """,
                (
                    category.name,
                    category.type,
                    category.monthly_budget,
                    1 if category.is_active else 0,
                )
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_by_id(self, category_id):
        """Επιστρέφει Category ή None."""
        conn = self.db.get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM categories WHERE id = ?",
                (category_id,)
            ).fetchone()
            return self.row_to_category(row)
        finally:
            conn.close()

    def get_by_name(self, name):
        """Επιστρέφει Category βάσει name ή None."""
        conn = self.db.get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM categories WHERE name = ?",
                (name,)
            ).fetchone()
            return self.row_to_category(row)
        finally:
            conn.close()

    def get_all(self, active_only=True, type_filter=None):
        """
        Επιστρέφει λίστα από Category objects.

        active_only: αν True, επιστρέφει μόνο ενεργές
        type_filter: 'income', 'expense', 'both' ή None
        """
        query = "SELECT * FROM categories WHERE 1=1"
        params = []

        if active_only:
            query += " AND is_active = 1"

        if type_filter is not None:
            # Αν ζητάς 'income', πάρε και τις 'both'
            if type_filter == "income":
                query += " AND type IN ('income', 'both')"
            elif type_filter == "expense":
                query += " AND type IN ('expense', 'both')"
            else:
                query += " AND type = ?"
                params.append(type_filter)

        query += " ORDER BY name"

        conn = self.db.get_connection()
        try:
            rows = conn.execute(query, params).fetchall()
            return [self.row_to_category(row) for row in rows]
        finally:
            conn.close()

    def update(self, category):
        """Ενημερώνει την κατηγορία και επιστρέφει True αν άλλαξε κάτι."""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                """
                UPDATE categories
                SET name = ?, type = ?, monthly_budget = ?, is_active = ?
                WHERE id = ?
                """,
                (
                    category.name,
                    category.type,
                    category.monthly_budget,
                    1 if category.is_active else 0,
                    category.id,
                )
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def soft_delete(self, category_id):
        """Soft delete: βάζει is_active = 0 και επιστρέφει True αν άλλαξε"""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                "UPDATE categories SET is_active = 0 WHERE id = ?",
                (category_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def hard_delete(self, category_id):
        """Διαγραφή. Επιστρέφει True αν διαγράφηκε."""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                "DELETE FROM categories WHERE id = ?",
                (category_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

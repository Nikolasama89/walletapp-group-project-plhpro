"""Repository για τον πίνακα transactions."""
from backend.models import Transaction


class TransactionRepository:
    """CRUD operations για συναλλαγές"""

    def __init__(self, database):
        self.db = database

    def row_to_transaction(self, row):
        """Μετατρέπει sqlite3.Row σε Transaction object"""
        if row is None:
            return None
        # Το category_name μπορεί να μην υπάρχει (αν δεν έγινε JOIN)
        category_name = None
        try:
            category_name = row["category_name"]
        except (IndexError, KeyError):
            pass

        return Transaction(
            id=row["id"],
            txn_type=row["txn_type"],
            amount=row["amount"],
            txn_date=row["txn_date"],
            category_id=row["category_id"],
            category_name=category_name,
            note=row["note"],
            created_at=row["created_at"],
        )

    def create(self, transaction):
        """Εισάγει νέα συναλλαγή και επιστρέφει το id της"""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO transactions
                    (txn_type, amount, category_id, txn_date, note)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    transaction.txn_type,
                    transaction.amount,
                    transaction.category_id,
                    transaction.txn_date,
                    transaction.note,
                )
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_by_id(self, txn_id):
        """Επιστρέφει Transaction με category_name ή None"""
        conn = self.db.get_connection()
        try:
            row = conn.execute(
                """
                SELECT t.*, c.name AS category_name
                FROM transactions t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.id = ?
                """,
                (txn_id,)
            ).fetchone()
            return self.row_to_transaction(row)
        finally:
            conn.close()

    def list_transactions(self, txn_type=None, category_id=None,
                          year=None, month=None,
                          start_date=None, end_date=None,
                          limit=None):
        """
        Επιστρέφει λίστα Transaction με τα φίλτρα.

        txn_type: 'income', 'expense', ή None για όλα
        category_id: φιλτράρισμα ανά κατηγορία
        year, month: φιλτράρισμα ανά έτος/μήνα
        start_date, end_date: χρονικό εύρος (YYYY-MM-DD)
        limit: max αριθμός αποτελεσμάτων
        """
        query = """
            SELECT t.*, c.name AS category_name
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE 1=1
        """
        params = []

        if txn_type is not None:
            query += " AND t.txn_type = ?"
            params.append(txn_type)

        if category_id is not None:
            query += " AND t.category_id = ?"
            params.append(category_id)

        if year is not None:
            query += " AND strftime('%Y', t.txn_date) = ?"
            params.append(str(year))

        if month is not None:
            # Padding με μηδενικά: 3 -> '03'
            query += " AND strftime('%m', t.txn_date) = ?"
            params.append("{:02d}".format(month))

        if start_date is not None:
            query += " AND t.txn_date >= ?"
            params.append(start_date)

        if end_date is not None:
            query += " AND t.txn_date <= ?"
            params.append(end_date)

        query += " ORDER BY t.txn_date DESC, t.id DESC"

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        conn = self.db.get_connection()
        try:
            rows = conn.execute(query, params).fetchall()
            return [self.row_to_transaction(row) for row in rows]
        finally:
            conn.close()

    def update(self, transaction):
        """Ενημερώνει συναλλαγή και επιστρέφει True αν άλλαξε κάτι"""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                """
                UPDATE transactions
                SET txn_type = ?, amount = ?, category_id = ?,
                    txn_date = ?, note = ?
                WHERE id = ?
                """,
                (
                    transaction.txn_type,
                    transaction.amount,
                    transaction.category_id,
                    transaction.txn_date,
                    transaction.note,
                    transaction.id,
                )
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, txn_id):
        """Διαγραφή συναλλαγής και επιστρέφει True αν διαγράφηκε"""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                "DELETE FROM transactions WHERE id = ?",
                (txn_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def sum_by_type(self, txn_type, year=None, month=None):
        """Επιστρέφει το συνολικό ποσό για έναν τύπο συναλλαγής."""
        query = "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE txn_type = ?"
        params = [txn_type]

        if year is not None:
            query += " AND strftime('%Y', txn_date) = ?"
            params.append(str(year))

        if month is not None:
            query += " AND strftime('%m', txn_date) = ?"
            params.append("{:02d}".format(month))

        conn = self.db.get_connection()
        try:
            result = conn.execute(query, params).fetchone()
            return result[0]
        finally:
            conn.close()

    def sum_by_category(self, txn_type, year=None, month=None):
        """
        Επιστρέφει λίστα από dicts με το σύνολο ανά κατηγορία.

        Format: [{"category_id": 1, "category_name": "Τρόφιμα", "total": 450.0}, ...]
        """
        query = """
            SELECT
                t.category_id,
                COALESCE(c.name, 'Χωρίς κατηγορία') AS category_name,
                SUM(t.amount) AS total
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.txn_type = ?
        """
        params = [txn_type]

        if year is not None:
            query += " AND strftime('%Y', t.txn_date) = ?"
            params.append(str(year))

        if month is not None:
            query += " AND strftime('%m', t.txn_date) = ?"
            params.append("{:02d}".format(month))

        query += " GROUP BY t.category_id, c.name ORDER BY total DESC"

        conn = self.db.get_connection()
        try:
            rows = conn.execute(query, params).fetchall()
            return [
                {
                    "category_id": row["category_id"],
                    "category_name": row["category_name"],
                    "total": row["total"],
                }
                for row in rows
            ]
        finally:
            conn.close()

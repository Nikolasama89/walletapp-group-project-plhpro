"""Repository για τον πίνακα tasks."""
from backend.models import Task


class TaskRepository:
    """CRUD operations για tasks υποχρεώσεις, επιθυμίες"""

    def __init__(self, database):
        self.db = database

    def row_to_task(self, row):
        """Μετατρέπει sqlite3.Row σε Task object."""
        if row is None:
            return None
        category_name = None
        try:
            category_name = row["category_name"]
        except (IndexError, KeyError):
            pass

        return Task(
            id=row["id"],
            task_type=row["task_type"],
            title=row["title"],
            amount=row["amount"],
            category_id=row["category_id"],
            category_name=category_name,
            due_date=row["due_date"],
            priority=row["priority"],
            status=row["status"],
            notify_days_before=row["notify_days_before"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, task):
        """Εισάγει νέο task και επιστρέφει το id του"""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO tasks
                    (task_type, title, amount, category_id, due_date,
                     priority, status, notify_days_before, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.task_type,
                    task.title,
                    task.amount,
                    task.category_id,
                    task.due_date,
                    task.priority,
                    task.status,
                    task.notify_days_before,
                    task.notes,
                )
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_by_id(self, task_id):
        """Επιστρέφει Task με category_name ή None"""
        conn = self.db.get_connection()
        try:
            row = conn.execute(
                """
                SELECT t.*, c.name AS category_name
                FROM tasks t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.id = ?
                """,
                (task_id,)
            ).fetchone()
            return self.row_to_task(row)
        finally:
            conn.close()

    def list_tasks(self, task_type=None, status=None, category_id=None,
                   due_before=None, due_after=None,
                   order_by="due_date"):
        """
        Επιστρέφει λίστα Task με τα φίλτρα.

        task_type: 'obligation', 'wish', ή None
        status: 'open', 'done', 'cancelled', ή None
        due_before / due_after: YYYY-MM-DD
        order_by: 'due_date', 'priority', 'created_at'
        """
        query = """
            SELECT t.*, c.name AS category_name
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE 1=1
        """
        params = []

        if task_type is not None:
            query += " AND t.task_type = ?"
            params.append(task_type)

        if status is not None:
            query += " AND t.status = ?"
            params.append(status)

        if category_id is not None:
            query += " AND t.category_id = ?"
            params.append(category_id)

        if due_before is not None:
            query += " AND t.due_date <= ?"
            params.append(due_before)

        if due_after is not None:
            query += " AND t.due_date >= ?"
            params.append(due_after)

        # Sorting
        if order_by == "priority":
            # 1=high -> εμφάνιση πρώτη
            query += " ORDER BY t.priority ASC, t.due_date ASC"
        elif order_by == "created_at":
            query += " ORDER BY t.created_at DESC"
        else:  # due_date (default)
            # NULL dates στο τέλος
            query += " ORDER BY (t.due_date IS NULL), t.due_date ASC, t.priority ASC"

        conn = self.db.get_connection()
        try:
            rows = conn.execute(query, params).fetchall()
            return [self.row_to_task(row) for row in rows]
        finally:
            conn.close()

    def update(self, task):
        """Ενημερώνει task και επιστρέφει True αν άλλαξε κάτι."""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                """
                UPDATE tasks
                SET task_type = ?, title = ?, amount = ?, category_id = ?,
                    due_date = ?, priority = ?, status = ?,
                    notify_days_before = ?, notes = ?
                WHERE id = ?
                """,
                (
                    task.task_type,
                    task.title,
                    task.amount,
                    task.category_id,
                    task.due_date,
                    task.priority,
                    task.status,
                    task.notify_days_before,
                    task.notes,
                    task.id,
                )
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def update_status(self, task_id, status):
        """Ενημερώνει μόνο το status και επιστρέφει True αν άλλαξε"""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                "UPDATE tasks SET status = ? WHERE id = ?",
                (status, task_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, task_id):
        """Διαγραφή task που επιστρέφει True αν διαγράφηκε"""
        conn = self.db.get_connection()
        try:
            cursor = conn.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

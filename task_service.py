"""Business logic για tasks υποχρεώσεις και επιθυμίες"""
from datetime import datetime, date

from backend.exceptions import NotFoundError, ValidationError
from backend.models import Task
from backend.repositories import CategoryRepository, TaskRepository


VALID_TASK_TYPES = ("obligation", "wish")
VALID_STATUSES = ("open", "done", "cancelled")
VALID_PRIORITIES = (1, 2, 3)


class TaskService:
    """Διαχείριση υποχρεώσεων και επιθυμιών με validation"""

    def __init__(self, database):
        self.repo = TaskRepository(database)
        self.cat_repo = CategoryRepository(database)

    def validate_task_type(self, task_type):
        if task_type not in VALID_TASK_TYPES:
            raise ValidationError(
                f"Μη έγκυρος τύπος task: '{task_type}'. Αποδεκτές: {VALID_TASK_TYPES}"
            )
        return task_type

    def validate_title(self, title):
        if title is None or title.strip() == "":
            raise ValidationError("Ο τίτλος είναι υποχρεωτικός.")
        title = title.strip()
        if len(title) > 100:
            raise ValidationError("Ο τίτλος είναι πολύ μεγάλος (max 100).")
        return title

    def validate_amount(self, amount):
        if amount is None:
            return None
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise ValidationError("Το ποσό πρέπει να είναι αριθμός.")
        if amount < 0:
            raise ValidationError("Το ποσό δεν μπορεί να είναι αρνητικό.")
        return round(amount, 2)

    def validate_due_date(self, due_date):
        if due_date is None:
            return None
        if isinstance(due_date, date):
            return due_date.strftime("%Y-%m-%d")
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
            return due_date
        except ValueError:
            raise ValidationError(
                f"Μη έγκυρη ημερομηνία: {due_date}. Χρησιμοποίησε YYYY-MM-DD"
            )

    def validate_priority(self, priority):
        try:
            priority = int(priority)
        except (TypeError, ValueError):
            raise ValidationError("Η προτεραιότητα πρέπει να είναι αριθμός.")
        if priority not in VALID_PRIORITIES:
            raise ValidationError(
                f"Μη έγκυρη προτεραιότητα: {priority}. Αποδεκτές: {VALID_PRIORITIES}"
            )
        return priority

    def validate_status(self, status):
        if status not in VALID_STATUSES:
            raise ValidationError(
                f"Μη έγκυρο status: {status}. Αποδεκτές: {VALID_STATUSES}"
            )
        return status

    def validate_category(self, category_id):
        if category_id is None:
            return None
        if self.cat_repo.get_by_id(category_id) is None:
            raise ValidationError(f"Δεν υπάρχει κατηγορία με id={category_id}")
        return category_id

    def create_task(
        self,
        task_type,
        title,
        amount=None,
        category_id=None,
        due_date=None,
        priority=2,
        notify_days_before=3,
        notes=None,
    ):
        task_type = self.validate_task_type(task_type)
        title = self.validate_title(title)
        amount = self.validate_amount(amount)
        category_id = self.validate_category(category_id)
        due_date = self.validate_due_date(due_date)
        priority = self.validate_priority(priority)

        if notify_days_before < 0:
            raise ValidationError("Τα notify_days_before δεν μπορεί να είναι αρνητικά.")

        if notes is not None:
            notes = str(notes).strip() or None

        task = Task(
            task_type=task_type,
            title=title,
            amount=amount,
            category_id=category_id,
            due_date=due_date,
            priority=priority,
            status="open",
            notify_days_before=notify_days_before,
            notes=notes,
        )

        new_id = self.repo.create(task)
        return self.repo.get_by_id(new_id)

    def get_task(self, task_id):
        task = self.repo.get_by_id(task_id)
        if task is None:
            raise NotFoundError(f"Δεν βρέθηκε task με id={task_id}")
        return task

    def update_task(
        self,
        task_id,
        task_type=None,
        title=None,
        amount=None,
        category_id=None,
        due_date=None,
        priority=None,
        status=None,
        notes=None,
    ):
        task = self.get_task(task_id)

        if task_type is not None:
            task.task_type = self.validate_task_type(task_type)
        if title is not None:
            task.title = self.validate_title(title)
        if amount is not None:
            task.amount = self.validate_amount(amount)
        if category_id is not None:
            task.category_id = self.validate_category(category_id)
        if due_date is not None:
            task.due_date = self.validate_due_date(due_date)
        if priority is not None:
            task.priority = self.validate_priority(priority)
        if status is not None:
            task.status = self.validate_status(status)
        if notes is not None:
            task.notes = str(notes).strip() or None

        self.repo.update(task)
        return self.repo.get_by_id(task_id)

    def mark_done(self, task_id):
        self.get_task(task_id)
        self.repo.update_status(task_id, "done")

    def delete_task(self, task_id):
        """
        Διαγράφει ένα task.

        Πρώτα γίνεται έλεγχος ότι υπάρχει το task.
        Αν δεν υπάρχει, πετάει NotFoundError.
        Αν υπάρχει, καλεί το repository για διαγραφή από τη βάση.
        """
        self.get_task(task_id)
        self.repo.delete(task_id)

    def list_tasks(self, task_type=None, status=None):
        if task_type is not None:
            self.validate_task_type(task_type)
        if status is not None:
            self.validate_status(status)

        return self.repo.list_tasks(task_type=task_type, status=status)

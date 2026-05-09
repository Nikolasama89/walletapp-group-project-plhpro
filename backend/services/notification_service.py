"""Ειδοποιήσεις για tasks"""
from datetime import date

from backend.repositories import TaskRepository


def get_days_remaining(item):
    """Επιστρέφει πόσες μέρες απομένουν για το task."""
    return item["days_remaining"]


def get_days_overdue(item):
    """Επιστρέφει πόσες μέρες έχει λήξει το task."""
    return item["days_overdue"]

class NotificationService:
    """Παραγωγή ειδοποιήσεων για επερχόμενα/ληγμένα tasks."""

    def __init__(self, database):
        self.task_repo = TaskRepository(database)

    def get_upcoming(self, reference_date=None):
        """
        Tasks που πλησιάζει η λήξη τους.
        Επιστρέφει: [{"task": Task, "days_remaining": int, "urgency": str}, ...]
        """
        if reference_date is None:
            reference_date = date.today()

        open_tasks = self.task_repo.list_tasks(status="open")

        notifications = []
        for task in open_tasks:
            if task.due_date is None:
                continue

            due = self.parse_date(task.due_date)
            if due is None:
                continue

            days_diff = (due - reference_date).days

            # Παραλείπουμε overdue (πάνε στο get_overdue)
            if days_diff < 0:
                continue

            # Είναι μέσα στο notify window;
            if days_diff <= task.notify_days_before:
                if days_diff <= 1:
                    urgency = "critical"
                else:
                    urgency = "normal"

                notifications.append({
                    "task": task,
                    "days_remaining": days_diff,
                    "urgency": urgency,
                })

        # Πιο επείγοντα πρώτα (μικρότερο days_remaining = πιο κοντά στη λήξη)
        notifications.sort(key=get_days_remaining)
        return notifications

    def get_overdue(self, reference_date=None):
        """
        Tasks που έχουν ήδη λήξει αλλά είναι ακόμα 'open'.
        Επιστρέφει: [{"task": Task, "days_overdue": int}, ...]
        """
        if reference_date is None:
            reference_date = date.today()

        open_tasks = self.task_repo.list_tasks(status="open")

        overdue = []
        for task in open_tasks:
            if task.due_date is None:
                continue

            due = self.parse_date(task.due_date)
            if due is None:
                continue

            days_diff = (due - reference_date).days
            if days_diff < 0:
                overdue.append({
                    "task": task,
                    "days_overdue": -days_diff,
                })

        # Πιο παλιά πρώτα (μεγαλύτερο days_overdue πρώτα)
        overdue.sort(key=get_days_overdue, reverse=True)
        return overdue

    def get_all_notifications(self, reference_date=None):
        """Πλήρης λίστα ειδοποιήσεων για dashboard."""
        overdue = self.get_overdue(reference_date)
        upcoming = self.get_upcoming(reference_date)
        return {
            "overdue": overdue,
            "upcoming": upcoming,
            "total_count": len(overdue) + len(upcoming),
        }

    def parse_date(self, date_str):
        """Μετατροπή 'YYYY-MM-DD' σε date object."""
        if date_str is None:
            return None
        try:
            parts = date_str.split("-")
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            return None

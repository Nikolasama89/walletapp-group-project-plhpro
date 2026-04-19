"""Κλάσεις που αναπαριστούν τα δεδομένα της εφαρμογής μας."""


class Category:
    """Κατηγορία εσόδου/εξόδου."""

    def __init__(self, name, type, id=None, monthly_budget=None,
                 is_active=True, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.type = type  # 'income', 'expense', ή 'both'
        self.monthly_budget = monthly_budget
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "Category(id={}, name='{}', type='{}')".format(
            self.id, self.name, self.type
        )


class Transaction:
    """Συναλλαγή έσοδο ή έξοδο που έγινε."""

    def __init__(self, txn_type, amount, txn_date, id=None,
                 category_id=None, category_name=None,
                 note=None, created_at=None):
        self.id = id
        self.txn_type = txn_type  # 'income' ή 'expense'
        self.amount = amount
        self.txn_date = txn_date  # string 'YYYY-MM-DD'
        self.category_id = category_id
        self.category_name = category_name  # γεμίζει με JOIN
        self.note = note
        self.created_at = created_at

    def __repr__(self):
        return "Transaction(id={}, type='{}', amount={}, date='{}')".format(
            self.id, self.txn_type, self.amount, self.txn_date
        )


class Task:
    """Υποχρέωση ή επιθυμία."""

    def __init__(self, task_type, title, id=None, amount=None,
                 category_id=None, category_name=None, due_date=None,
                 priority=2, status="open", notify_days_before=3,
                 notes=None, created_at=None, updated_at=None):
        self.id = id
        self.task_type = task_type  # 'obligation' ή 'wish'
        self.title = title
        self.amount = amount
        self.category_id = category_id
        self.category_name = category_name
        self.due_date = due_date  # string 'YYYY-MM-DD' ή None
        self.priority = priority  # 1=high, 2=medium, 3=low
        self.status = status  # 'open', 'done', ή 'cancelled'
        self.notify_days_before = notify_days_before
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "Task(id={}, type='{}', title='{}', status='{}')".format(
            self.id, self.task_type, self.title, self.status
        )


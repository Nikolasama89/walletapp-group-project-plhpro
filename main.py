import tkinter as tk

from backend.database import Database
from backend.services import (
    CategoryService,
    TransactionService,
    TaskService,
    BudgetService,
    StatsService,
    NotificationService,
)

from gui.main_window import MainWindow


def main():
    database = Database()

    category_service = CategoryService(database)
    transaction_service = TransactionService(database)
    task_service = TaskService(database)
    budget_service = BudgetService(database)
    stats_service = StatsService(database)
    notification_service = NotificationService(database)

    root = tk.Tk()

    MainWindow(
        root,
        category_service=category_service,
        transaction_service=transaction_service,
        task_service=task_service,
        budget_service=budget_service,
        stats_service=stats_service,
        notification_service=notification_service,
    )

    root.mainloop()


if __name__ == "__main__":
    main()
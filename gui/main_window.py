from tkinter import ttk
from gui.categories_tab import CategoriesTab
from gui.tasks_tab import TasksTab
from gui.budget_tab import BudgetTab
from gui.stats_tab import StatsTab
from gui.notifications_tab import NotificationsTab
from gui.overview_tab import OverviewTab
from gui.transactions_tab import TransactionsTab


class MainWindow:
    def __init__(
        self,
        root,
        category_service,
        transaction_service,
        task_service,
        budget_service,
        stats_service,
        notification_service,
    ):
        self.root = root

        self.category_service = category_service
        self.transaction_service = transaction_service
        self.task_service = task_service
        self.budget_service = budget_service
        self.stats_service = stats_service
        self.notification_service = notification_service

        self.root.title("Wallet App")
        self.root.geometry("1000x650")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        self.transactions_tab = TransactionsTab(
            self.notebook,
            transaction_service=self.transaction_service,
            category_service=self.category_service,
        )

        self.categories_tab = CategoriesTab(
            self.notebook,
            category_service=self.category_service,
        )

        self.tasks_tab = TasksTab(
            self.notebook,
            task_service=self.task_service,
            category_service=self.category_service,
        )

        self.budget_tab = BudgetTab(
            self.notebook,
            budget_service=self.budget_service,
        )

        self.stats_tab = StatsTab(
            self.notebook,
            stats_service=self.stats_service,
        )

        self.notifications_tab = NotificationsTab(
            self.notebook,
            notification_service=self.notification_service,
        )

        self.overview_tab = OverviewTab(
            self.notebook,
            transaction_service=self.transaction_service,
            category_service=self.category_service,
            stats_service=self.stats_service,
        )

        self.notebook.add(self.transactions_tab, text="Συναλλαγές")
        self.notebook.add(self.categories_tab, text="Κατηγορίες")
        self.notebook.add(self.tasks_tab, text="Υποχρεώσεις")
        self.notebook.add(self.budget_tab, text="Budgets")
        self.notebook.add(self.stats_tab, text="Στατιστικά")
        self.notebook.add(self.notifications_tab, text="Ειδοποιήσεις")
        self.notebook.add(self.overview_tab, text="Επισκόπηση")


from tkinter import ttk

from gui.transactions_tab import TransactionsTab
from gui.categories_tab import CategoriesTab
from gui.reports_tab import ReportsTab
from gui.overview_tab import OverviewTab


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallet App")
        self.root.geometry("900x600")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        self.transactions_tab = TransactionsTab(self.notebook)
        self.categories_tab = CategoriesTab(self.notebook)
        self.reports_tab = ReportsTab(self.notebook)
        self.overview_tab = OverviewTab(self.notebook)

        self.notebook.add(self.transactions_tab, text="Συναλλαγές")
        self.notebook.add(self.categories_tab, text="Κατηγορίες")
        self.notebook.add(self.reports_tab, text="Αναφορές")
        self.notebook.add(self.overview_tab, text="Επισκόπηση")
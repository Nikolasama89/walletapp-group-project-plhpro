from tkinter import ttk

from gui.transactions_tab import TransactionsTab
from gui.categories_tab import CategoriesTab
from gui.reports_tab import ReportsTab


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallet App")
        self.root.geometry("900x600")

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # Create tabs
        self.transactions_tab = TransactionsTab(self.notebook)
        self.categories_tab = CategoriesTab(self.notebook)
        self.reports_tab = ReportsTab(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.transactions_tab, text="Συναλλαγές")
        self.notebook.add(self.categories_tab, text="Κατηγορίες")
        self.notebook.add(self.reports_tab, text="Αναφορές")

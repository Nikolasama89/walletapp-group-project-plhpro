import tkinter as tk
from tkinter import ttk

from gui.transactions_tab import TransactionsTab
from gui.categories_tab import CategoriesTab

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallet App")
        self.root.geometry("800x500")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        self.transactions_tab = TransactionsTab(self.notebook)
        self.categories_tab = CategoriesTab(self.notebook)

        self.notebook.add(self.transactions_tab, text="Συναλλαγές")
        self.notebook.add(self.categories_tab, text="Κατηγορίες")
        from gui.reports_tab import ReportsTab
        self.reports_tab = ReportsTab(self.notebook)
        self.notebook.add(self.reports_tab, text="Αναφορές")
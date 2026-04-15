from tkinter import ttk

class CategoriesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(self, text="Categories Tab").grid(row=0, column=0, padx=20, pady=20)
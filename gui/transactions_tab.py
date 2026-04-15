from tkinter import ttk

class TransactionsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Amount
        ttk.Label(self, text="Ποσό (€):").grid(row=0, column=0, padx=10, pady=10)
        self.amount_entry = ttk.Entry(self)
        self.amount_entry.grid(row=0, column=1)

        # Type
        ttk.Label(self, text="Τύπος:").grid(row=1, column=0, padx=10)
        self.type_combo = ttk.Combobox(self, values=["income", "expense"])
        self.type_combo.grid(row=1, column=1)
        self.type_combo.current(0)

        # Save button
        self.save_button = ttk.Button(self, text="Αποθήκευση", command=self.save_transaction)
        self.save_button.grid(row=2, column=1, pady=20)

    def save_transaction(self):
        amount = self.amount_entry.get()
        print("Saved transaction:", amount)
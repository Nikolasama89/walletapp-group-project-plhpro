from tkinter import ttk, messagebox
from services.transaction_service import add_transaction as service_add_transaction


class TransactionsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Title
        ttk.Label(
            self,
            text="Καταχώρηση Συναλλαγής",
            font=("Arial", 12)
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Amount
        ttk.Label(self, text="Ποσό (€):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(self)
        self.amount_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Type
        ttk.Label(self, text="Τύπος:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.type_combo = ttk.Combobox(
            self,
            values=["income", "expense"],
            state="readonly"
        )
        self.type_combo.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.type_combo.current(0)

        # Category
        ttk.Label(self, text="Κατηγορία:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.category_entry = ttk.Entry(self)
        self.category_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Date
        ttk.Label(self, text="Ημερομηνία:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.date_entry = ttk.Entry(self)
        self.date_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Description
        ttk.Label(self, text="Περιγραφή:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.description_entry = ttk.Entry(self)
        self.description_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        # Save button
        self.save_button = ttk.Button(
            self,
            text="Αποθήκευση",
            command=self.save_transaction
        )
        self.save_button.grid(row=6, column=1, pady=15, sticky="e")

        # Make second column stretch
        self.columnconfigure(1, weight=1)

    def save_transaction(self):
        amount_text = self.amount_entry.get().strip()
        transaction_type = self.type_combo.get().strip()
        category = self.category_entry.get().strip()
        date = self.date_entry.get().strip()
        description = self.description_entry.get().strip()

        # Validation for amount
        if not amount_text:
            messagebox.showerror("Σφάλμα", "Το ποσό είναι υποχρεωτικό")
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                messagebox.showerror("Σφάλμα", "Το ποσό πρέπει να είναι θετικός αριθμός")
                return
        except ValueError:
            messagebox.showerror("Σφάλμα", "Το ποσό πρέπει να είναι αριθμός")
            return

        # Basic validation for date
        if not date:
            messagebox.showerror("Σφάλμα", "Η ημερομηνία είναι υποχρεωτική")
            return

        # Call service
        #service_add_transaction(amount, transaction_type, category, date, description)

        # Clear fields
        self.amount_entry.delete(0, "end")
        self.type_combo.current(0)
        self.category_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.description_entry.delete(0, "end")

        messagebox.showinfo("Επιτυχία", "Η συναλλαγή αποθηκεύτηκε")
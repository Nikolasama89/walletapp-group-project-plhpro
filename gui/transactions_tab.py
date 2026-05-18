from tkinter import ttk, messagebox

from backend.exceptions import ValidationError, NotFoundError


class TransactionsTab(ttk.Frame):
    def __init__(self, parent, transaction_service, category_service):
        super().__init__(parent)

        self.transaction_service = transaction_service
        self.category_service = category_service

        self.category_map = {}

        ttk.Label(
            self,
            text="Καταχώρηση Συναλλαγής",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Ποσό
        ttk.Label(self, text="Ποσό (€):").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.amount_entry = ttk.Entry(self)
        self.amount_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Τύπος συναλλαγής
        ttk.Label(self, text="Τύπος:").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.type_combo = ttk.Combobox(
            self,
            values=["income", "expense"],
            state="readonly"
        )
        self.type_combo.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.type_combo.current(1)
        self.type_combo.bind("<<ComboboxSelected>>", self.load_categories)

        # Κατηγορία
        ttk.Label(self, text="Κατηγορία:").grid(
            row=3, column=0, padx=10, pady=5, sticky="w"
        )
        self.category_combo = ttk.Combobox(
            self,
            state="readonly"
        )
        self.category_combo.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Ημερομηνία
        ttk.Label(self, text="Ημερομηνία (YYYY-MM-DD):").grid(
            row=4, column=0, padx=10, pady=5, sticky="w"
        )
        self.date_entry = ttk.Entry(self)
        self.date_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Σημείωση
        ttk.Label(self, text="Σημείωση:").grid(
            row=5, column=0, padx=10, pady=5, sticky="w"
        )
        self.note_entry = ttk.Entry(self)
        self.note_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        # Κουμπί αποθήκευσης
        self.save_button = ttk.Button(
            self,
            text="Αποθήκευση",
            command=self.save_transaction
        )
        self.save_button.grid(row=6, column=1, pady=15, sticky="e")

        # Πίνακας συναλλαγών
        self.transactions_table = ttk.Treeview(
            self,
            columns=("id", "date", "type", "category", "amount", "note"),
            show="headings",
            height=10
        )

        self.transactions_table.heading("id", text="ID")
        self.transactions_table.heading("date", text="Ημερομηνία")
        self.transactions_table.heading("type", text="Τύπος")
        self.transactions_table.heading("category", text="Κατηγορία")
        self.transactions_table.heading("amount", text="Ποσό (€)")
        self.transactions_table.heading("note", text="Σημείωση")

        self.transactions_table.column("id", width=50, anchor="center")
        self.transactions_table.column("date", width=110, anchor="center")
        self.transactions_table.column("type", width=90, anchor="center")
        self.transactions_table.column("category", width=140)
        self.transactions_table.column("amount", width=100, anchor="center")
        self.transactions_table.column("note", width=180)

        self.transactions_table.grid(
            row=7,
            column=0,
            columnspan=2,
            padx=10,
            pady=10,
            sticky="nsew"
        )

        self.columnconfigure(1, weight=1)
        self.rowconfigure(7, weight=1)

        self.load_categories()
        self.load_transactions()

    def load_categories(self, event=None):
        txn_type = self.type_combo.get()

        try:
            categories = self.category_service.get_all_categories(
                active_only=True,
                type_filter=txn_type
            )

            self.category_map = {"Χωρίς κατηγορία": None}

            for category in categories:
                self.category_map[category.name] = category.id

            self.category_combo["values"] = list(self.category_map.keys())
            self.category_combo.current(0)

        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def save_transaction(self):
        amount = self.amount_entry.get().strip()
        txn_type = self.type_combo.get().strip()
        category_name = self.category_combo.get().strip()
        txn_date = self.date_entry.get().strip()
        note = self.note_entry.get().strip()

        category_id = self.category_map.get(category_name)

        if txn_date == "":
            txn_date = None

        if note == "":
            note = None

        try:
            self.transaction_service.create_transaction(
                txn_type=txn_type,
                amount=amount,
                category_id=category_id,
                txn_date=txn_date,
                note=note
            )

            messagebox.showinfo("Επιτυχία", "Η συναλλαγή αποθηκεύτηκε.")

            self.clear_form()
            self.load_categories()
            self.load_transactions()

        except ValidationError as e:
            messagebox.showerror("Σφάλμα εγκυρότητας", str(e))

        except NotFoundError as e:
            messagebox.showerror("Δεν βρέθηκε", str(e))

        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def load_transactions(self):
        for item in self.transactions_table.get_children():
            self.transactions_table.delete(item)

        try:
            transactions = self.transaction_service.list_transactions()

            for txn in transactions:
                amount = "{:.2f}".format(txn.amount)

                self.transactions_table.insert(
                    "",
                    "end",
                    values=(
                        txn.id,
                        txn.txn_date,
                        txn.txn_type,
                        txn.category_name if txn.category_name else "",
                        amount,
                        txn.note if txn.note else ""
                    )
                )

        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def clear_form(self):
        self.amount_entry.delete(0, "end")
        self.type_combo.current(1)
        self.load_categories()
        self.date_entry.delete(0, "end")
        self.note_entry.delete(0, "end")

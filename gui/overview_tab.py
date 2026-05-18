from tkinter import ttk, messagebox

from backend.exceptions import ValidationError, NotFoundError


class OverviewTab(ttk.Frame):
    def __init__(self, parent, transaction_service, category_service, stats_service):
        super().__init__(parent)

        self.transaction_service = transaction_service
        self.category_service = category_service
        self.stats_service = stats_service

        self.category_map = {}

        ttk.Label(
            self,
            text="Επισκόπηση Συναλλαγών",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        # ===== Filters frame =====
        filters_frame = ttk.LabelFrame(self, text="Φίλτρα")
        filters_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(filters_frame, text="Τύπος:").grid(
            row=0, column=0, padx=5, pady=5
        )

        self.type_combo = ttk.Combobox(
            filters_frame,
            values=["all", "income", "expense"],
            state="readonly",
            width=12
        )
        self.type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.type_combo.current(0)

        self.type_combo.bind("<<ComboboxSelected>>", self.load_categories)

        ttk.Label(filters_frame, text="Κατηγορία:").grid(
            row=0, column=2, padx=5, pady=5
        )

        self.category_combo = ttk.Combobox(
            filters_frame,
            state="readonly",
            width=18
        )
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(filters_frame, text="Έτος:").grid(
            row=1, column=0, padx=5, pady=5
        )

        self.year_entry = ttk.Entry(filters_frame, width=12)
        self.year_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(filters_frame, text="Μήνας:").grid(
            row=1, column=2, padx=5, pady=5
        )

        self.month_entry = ttk.Entry(filters_frame, width=12)
        self.month_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(
            filters_frame,
            text="Εφαρμογή",
            command=self.apply_filters
        ).grid(row=0, column=4, padx=10, pady=5)

        ttk.Button(
            filters_frame,
            text="Ανανέωση",
            command=self.refresh
        ).grid(row=1, column=4, padx=10, pady=5)

        # ===== Summary frame =====
        summary_frame = ttk.LabelFrame(self, text="Σύνοψη")
        summary_frame.pack(fill="x", padx=10, pady=10)

        self.income_label = ttk.Label(summary_frame, text="Έσοδα: 0.00 €")
        self.income_label.pack(side="left", padx=15, pady=10)

        self.expense_label = ttk.Label(summary_frame, text="Έξοδα: 0.00 €")
        self.expense_label.pack(side="left", padx=15, pady=10)

        self.balance_label = ttk.Label(summary_frame, text="Υπόλοιπο: 0.00 €")
        self.balance_label.pack(side="left", padx=15, pady=10)

        self.filtered_total_label = ttk.Label(
            summary_frame,
            text="Σύνολο φίλτρου: 0.00 €"
        )
        self.filtered_total_label.pack(side="left", padx=15, pady=10)

        # ===== Results table =====
        table_frame = ttk.LabelFrame(self, text="Αποτελέσματα")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("id", "date", "type", "category", "amount", "note"),
            show="headings",
            height=12
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Ημερομηνία")
        self.tree.heading("type", text="Τύπος")
        self.tree.heading("category", text="Κατηγορία")
        self.tree.heading("amount", text="Ποσό")
        self.tree.heading("note", text="Σημείωση")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("date", width=110, anchor="center")
        self.tree.column("type", width=90, anchor="center")
        self.tree.column("category", width=150)
        self.tree.column("amount", width=100, anchor="center")
        self.tree.column("note", width=220)

        self.tree.pack(fill="both", expand=True)

        self.load_categories()
        self.apply_filters()

    def load_categories(self, event=None):
        selected_type = self.type_combo.get()

        if selected_type == "all":
            type_filter = None
        else:
            type_filter = selected_type

        try:
            categories = self.category_service.get_all_categories(
                active_only=True,
                type_filter=type_filter
            )

            self.category_map = {"Όλες": None}

            for category in categories:
                self.category_map[category.name] = category.id

            self.category_combo["values"] = list(self.category_map.keys())
            self.category_combo.current(0)

        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def apply_filters(self):
        selected_type = self.type_combo.get()
        selected_category = self.category_combo.get()

        year_text = self.year_entry.get().strip()
        month_text = self.month_entry.get().strip()

        if selected_type == "all":
            txn_type = None
        else:
            txn_type = selected_type

        category_id = self.category_map.get(selected_category)

        year = None if year_text == "" else year_text
        month = None if month_text == "" else month_text

        try:
            if month is not None:
                month = int(month)

            transactions = self.transaction_service.list_transactions(
                txn_type=txn_type,
                category_id=category_id,
                year=year,
                month=month
            )

            self.clear_table()

            filtered_total = 0.0

            for txn in transactions:
                amount = float(txn.amount)
                filtered_total += amount

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        txn.id,
                        txn.txn_date,
                        txn.txn_type,
                        txn.category_name if txn.category_name else "",
                        "{:.2f}".format(amount),
                        txn.note if txn.note else ""
                    )
                )

            self.filtered_total_label.config(
                text="Σύνολο φίλτρου: {:.2f} €".format(filtered_total)
            )

            self.load_summary(year, month)

        except ValueError:
            messagebox.showerror("Σφάλμα", "Ο μήνας πρέπει να είναι αριθμός.")

        except ValidationError as e:
            messagebox.showerror("Σφάλμα εγκυρότητας", str(e))

        except NotFoundError as e:
            messagebox.showerror("Δεν βρέθηκε", str(e))

        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def load_summary(self, year, month):
        try:
            balance = self.stats_service.get_balance(
                year=year,
                month=month
            )

            self.income_label.config(
                text="Έσοδα: {:.2f} €".format(balance["income"])
            )

            self.expense_label.config(
                text="Έξοδα: {:.2f} €".format(balance["expense"])
            )

            self.balance_label.config(
                text="Υπόλοιπο: {:.2f} €".format(balance["balance"])
            )

        except ValidationError as e:
            messagebox.showerror("Σφάλμα εγκυρότητας", str(e))

        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def refresh(self):
        self.load_categories()
        self.apply_filters()

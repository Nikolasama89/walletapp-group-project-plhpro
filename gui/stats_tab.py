from tkinter import ttk, messagebox

from backend.exceptions import ValidationError


class StatsTab(ttk.Frame):
    def __init__(self, parent, stats_service):
        super().__init__(parent)

        self.stats_service = stats_service

        ttk.Label(
            self,
            text="Στατιστικά",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        filters_frame = ttk.LabelFrame(self, text="Φίλτρα")
        filters_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(filters_frame, text="Έτος:").grid(row=0, column=0, padx=5, pady=5)
        self.year_entry = ttk.Entry(filters_frame, width=10)
        self.year_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filters_frame, text="Μήνας:").grid(row=0, column=2, padx=5, pady=5)
        self.month_entry = ttk.Entry(filters_frame, width=10)
        self.month_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(
            filters_frame,
            text="Υπολογισμός",
            command=self.load_stats
        ).grid(row=0, column=4, padx=10, pady=5)

        summary_frame = ttk.LabelFrame(self, text="Ισοζύγιο")
        summary_frame.pack(fill="x", padx=10, pady=10)

        self.income_label = ttk.Label(summary_frame, text="Έσοδα: 0.00 €")
        self.income_label.pack(side="left", padx=15, pady=10)

        self.expense_label = ttk.Label(summary_frame, text="Έξοδα: 0.00 €")
        self.expense_label.pack(side="left", padx=15, pady=10)

        self.balance_label = ttk.Label(summary_frame, text="Υπόλοιπο: 0.00 €")
        self.balance_label.pack(side="left", padx=15, pady=10)

        distribution_frame = ttk.LabelFrame(self, text="Κατανομή εξόδων ανά κατηγορία")
        distribution_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.distribution_table = ttk.Treeview(
            distribution_frame,
            columns=("category", "total", "percentage"),
            show="headings",
            height=10
        )

        self.distribution_table.heading("category", text="Κατηγορία")
        self.distribution_table.heading("total", text="Σύνολο")
        self.distribution_table.heading("percentage", text="Ποσοστό")

        self.distribution_table.pack(fill="both", expand=True)

        self.load_stats()

    def load_stats(self):
        year = self.year_entry.get().strip()
        month = self.month_entry.get().strip()

        year = None if year == "" else year
        month = None if month == "" else month

        try:
            balance = self.stats_service.get_balance(year=year, month=month)

            self.income_label.config(text="Έσοδα: {:.2f} €".format(balance["income"]))
            self.expense_label.config(text="Έξοδα: {:.2f} €".format(balance["expense"]))
            self.balance_label.config(text="Υπόλοιπο: {:.2f} €".format(balance["balance"]))

            self.load_distribution(year, month)

        except ValidationError as e:
            messagebox.showerror("Σφάλμα εγκυρότητας", str(e))
        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def load_distribution(self, year, month):
        for item in self.distribution_table.get_children():
            self.distribution_table.delete(item)

        data = self.stats_service.get_category_distribution(
            txn_type="expense",
            year=year,
            month=month
        )

        for row in data:
            self.distribution_table.insert(
                "",
                "end",
                values=(
                    row["category_name"],
                    "{:.2f}".format(row["total"]),
                    "{:.2f}%".format(row["percentage"]),
                )
            )
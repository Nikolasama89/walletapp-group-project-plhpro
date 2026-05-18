from tkinter import ttk, messagebox


class BudgetTab(ttk.Frame):
    def __init__(self, parent, budget_service):
        super().__init__(parent)

        self.budget_service = budget_service

        ttk.Label(
            self,
            text="Παρακολούθηση Budget",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        ttk.Button(
            self,
            text="Ανανέωση",
            command=self.load_budget_statuses
        ).pack(pady=5)

        self.budget_table = ttk.Treeview(
            self,
            columns=("category", "budget", "spent", "remaining", "percentage", "status"),
            show="headings",
            height=12
        )

        self.budget_table.heading("category", text="Κατηγορία")
        self.budget_table.heading("budget", text="Budget")
        self.budget_table.heading("spent", text="Ξοδεύτηκαν")
        self.budget_table.heading("remaining", text="Υπόλοιπο")
        self.budget_table.heading("percentage", text="Ποσοστό")
        self.budget_table.heading("status", text="Status")

        self.budget_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_budget_statuses()

    def load_budget_statuses(self):
        for item in self.budget_table.get_children():
            self.budget_table.delete(item)

        try:
            statuses = self.budget_service.get_all_budget_statuses()

            for item in statuses:
                budget = "" if item["budget"] is None else "{:.2f}".format(item["budget"])
                spent = "{:.2f}".format(item["spent"])
                remaining = "" if item["remaining"] is None else "{:.2f}".format(item["remaining"])
                percentage = "" if item["percentage"] is None else "{:.2f}%".format(item["percentage"])

                self.budget_table.insert(
                    "",
                    "end",
                    values=(
                        item["category_name"],
                        budget,
                        spent,
                        remaining,
                        percentage,
                        item["status"],
                    )
                )

        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))
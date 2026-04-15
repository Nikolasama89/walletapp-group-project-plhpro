from tkinter import ttk, messagebox
from services.category_service import add_category as service_add_category


class CategoriesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Title
        ttk.Label(
            self,
            text="Διαχείριση Κατηγοριών",
            font=("Arial", 12)
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Name
        ttk.Label(self, text="Όνομα κατηγορίας:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Budget
        ttk.Label(self, text="Μηνιαίο budget (€):").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.budget_entry = ttk.Entry(self)
        self.budget_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Add button
        ttk.Button(
            self,
            text="Προσθήκη",
            command=self.add_category
        ).grid(row=3, column=1, pady=10, sticky="e")

        # Treeview with 2 columns
        self.categories_list = ttk.Treeview(
            self,
            columns=("name", "budget"),
            show="headings",
            height=8
        )
        self.categories_list.heading("name", text="Κατηγορία")
        self.categories_list.heading("budget", text="Budget (€)")

        self.categories_list.column("name", width=180)
        self.categories_list.column("budget", width=120, anchor="center")

        self.categories_list.grid(
            row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )

        # Make column 1 stretch a bit
        self.columnconfigure(1, weight=1)

    def add_category(self):
        name = self.name_entry.get().strip()
        budget_text = self.budget_entry.get().strip()

        # Validation for name
        if not name:
            messagebox.showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό")
            return

        # Validation for budget
        if budget_text == "":
            budget = 0.0
        else:
            try:
                budget = float(budget_text)
                if budget < 0:
                    messagebox.showerror("Σφάλμα", "Το budget δεν μπορεί να είναι αρνητικό")
                    return
            except ValueError:
                messagebox.showerror("Σφάλμα", "Το budget πρέπει να είναι αριθμός")
                return

        # Call service
        service_add_category(name, budget)

        # Show in GUI list
        self.categories_list.insert("", "end", values=(name, f"{budget:.2f}"))

        # Clear fields
        self.name_entry.delete(0, "end")
        self.budget_entry.delete(0, "end")

        messagebox.showinfo("Επιτυχία", "Η κατηγορία προστέθηκε")
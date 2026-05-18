from tkinter import ttk, messagebox

from backend.exceptions import ValidationError, DuplicateError, NotFoundError


class CategoriesTab(ttk.Frame):
    def __init__(self, parent, category_service):
        super().__init__(parent)

        self.category_service = category_service

        ttk.Label(
            self,
            text="Διαχείριση Κατηγοριών",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Όνομα κατηγορίας
        ttk.Label(self, text="Όνομα κατηγορίας:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Τύπος κατηγορίας
        ttk.Label(self, text="Τύπος:").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.type_combo = ttk.Combobox(
            self,
            values=["income", "expense", "both"],
            state="readonly"
        )
        self.type_combo.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.type_combo.current(1)

        # Budget
        ttk.Label(self, text="Μηνιαίο budget (€):").grid(
            row=3, column=0, padx=10, pady=5, sticky="w"
        )
        self.budget_entry = ttk.Entry(self)
        self.budget_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Κουμπί προσθήκης
        ttk.Button(
            self,
            text="Προσθήκη",
            command=self.add_category
        ).grid(row=4, column=1, pady=10, sticky="e")

        # Πίνακας κατηγοριών
        self.categories_list = ttk.Treeview(
            self,
            columns=("id", "name", "type", "budget"),
            show="headings",
            height=10
        )

        self.categories_list.heading("id", text="ID")
        self.categories_list.heading("name", text="Κατηγορία")
        self.categories_list.heading("type", text="Τύπος")
        self.categories_list.heading("budget", text="Budget (€)")

        self.categories_list.column("id", width=50, anchor="center")
        self.categories_list.column("name", width=180)
        self.categories_list.column("type", width=100, anchor="center")
        self.categories_list.column("budget", width=120, anchor="center")

        self.categories_list.grid(
            row=5,
            column=0,
            columnspan=2,
            padx=10,
            pady=10,
            sticky="nsew"
        )

        self.columnconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)

        self.load_categories()

    def add_category(self):
        name = self.name_entry.get().strip()
        category_type = self.type_combo.get().strip()
        budget_text = self.budget_entry.get().strip()

        monthly_budget = None if budget_text == "" else budget_text

        try:
            self.category_service.create_category(
                name=name,
                type=category_type,
                monthly_budget=monthly_budget
            )

            messagebox.showinfo("Επιτυχία", "Η κατηγορία προστέθηκε.")

            self.clear_form()
            self.load_categories()

        except ValidationError as e:
            messagebox.showerror("Σφάλμα εγκυρότητας", str(e))

        except DuplicateError as e:
            messagebox.showerror("Διπλότυπη κατηγορία", str(e))

        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def load_categories(self):
        for item in self.categories_list.get_children():
            self.categories_list.delete(item)

        try:
            categories = self.category_service.get_all_categories()

            for category in categories:
                budget = ""
                if category.monthly_budget is not None:
                    budget = "{:.2f}".format(category.monthly_budget)

                self.categories_list.insert(
                    "",
                    "end",
                    values=(
                        category.id,
                        category.name,
                        category.type,
                        budget
                    )
                )

        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def clear_form(self):
        self.name_entry.delete(0, "end")
        self.type_combo.current(1)
        self.budget_entry.delete(0, "end")
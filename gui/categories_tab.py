from tkinter import ttk, messagebox

class CategoriesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Title
        ttk.Label(self, text="Διαχείριση Κατηγοριών", font=("Arial", 12)).grid(
            row=0, column=0, columnspan=2, pady=10
        )

        # Name
        ttk.Label(self, text="Όνομα κατηγορίας:").grid(row=1, column=0, padx=10, pady=5)
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=1, column=1)

        # Budget
        ttk.Label(self, text="Μηνιαίο budget (€):").grid(row=2, column=0, padx=10, pady=5)
        self.budget_entry = ttk.Entry(self)
        self.budget_entry.grid(row=2, column=1)

        # Add button
        ttk.Button(self, text="Προσθήκη", command=self.add_category).grid(
            row=3, column=1, pady=10, sticky="e"
        )

        # Listbox
        self.categories_list = ttk.Treeview(self, columns=("budget",), show="headings")
        self.categories_list.heading("budget", text="Budget (€)")
        self.categories_list.grid(row=4, column=0, columnspan=2, pady=10)

    def add_category(self):
        name = self.name_entry.get()
        budget = self.budget_entry.get()

        if not name:
            messagebox.showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό")
            return

        self.categories_list.insert("", "end", values=(f"{name} - {budget}€",))

        self.name_entry.delete(0, "end")
        self.budget_entry.delete(0, "end")

        messagebox.showinfo("Επιτυχία", "Η κατηγορία προστέθηκε")
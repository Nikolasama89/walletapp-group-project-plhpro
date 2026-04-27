from tkinter import ttk


class OverviewTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(
            self,
            text="Επισκόπηση Συναλλαγών",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        # ===== Filters frame =====
        filters_frame = ttk.LabelFrame(self, text="Φίλτρα")
        filters_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(filters_frame, text="Τύπος:").grid(row=0, column=0, padx=5, pady=5)
        self.type_combo = ttk.Combobox(
            filters_frame,
            values=["all", "income", "expense"],
            state="readonly"
        )
        self.type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.type_combo.current(0)

        ttk.Label(filters_frame, text="Κατηγορία:").grid(row=0, column=2, padx=5, pady=5)
        self.category_combo = ttk.Combobox(
            filters_frame,
            values=["Όλες", "Τρόφιμα", "Μισθός", "Μετακινήσεις"],
            state="readonly"
        )
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.current(0)

        ttk.Button(
            filters_frame,
            text="Εφαρμογή",
            command=self.apply_filters
        ).grid(row=0, column=4, padx=10, pady=5)

        # ===== Summary frame =====
        summary_frame = ttk.LabelFrame(self, text="Σύνοψη")
        summary_frame.pack(fill="x", padx=10, pady=10)

        self.total_label = ttk.Label(summary_frame, text="Συνολικό ποσό: 0.00 €")
        self.total_label.pack(padx=10, pady=10)

        # ===== Results table =====
        table_frame = ttk.LabelFrame(self, text="Αποτελέσματα")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("date", "type", "category", "amount", "note"),
            show="headings"
        )

        self.tree.heading("date", text="Ημερομηνία")
        self.tree.heading("type", text="Τύπος")
        self.tree.heading("category", text="Κατηγορία")
        self.tree.heading("amount", text="Ποσό")
        self.tree.heading("note", text="Σημείωση")

        self.tree.pack(fill="both", expand=True)

    def apply_filters(self):
        selected_type = self.type_combo.get()
        selected_category = self.category_combo.get()

        # Προσωρινά fake δεδομένα για να δούμε τη λογική
        fake_rows = [
            ("2026-04-01", "expense", "Τρόφιμα", 50.0, "Σούπερ μάρκετ"),
            ("2026-04-02", "income", "Μισθός", 1200.0, "Μηνιαίος μισθός"),
            ("2026-04-03", "expense", "Μετακινήσεις", 20.0, "Βενζίνη"),
        ]

        filtered_rows = []

        for row in fake_rows:
            row_date, row_type, row_category, row_amount, row_note = row

            if selected_type != "all" and row_type != selected_type:
                continue

            if selected_category != "Όλες" and row_category != selected_category:
                continue

            filtered_rows.append(row)

        # Καθάρισε παλιό περιεχόμενο
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Πρόσθεσε φιλτραρισμένα αποτελέσματα
        total = 0.0
        for row in filtered_rows:
            self.tree.insert("", "end", values=row)
            total += row[3]

        self.total_label.config(text="Συνολικό ποσό: {:.2f} €".format(total))
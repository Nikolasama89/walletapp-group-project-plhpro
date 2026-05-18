from tkinter import ttk, messagebox

from backend.exceptions import ValidationError, NotFoundError


class TasksTab(ttk.Frame):
    def __init__(self, parent, task_service, category_service):
        super().__init__(parent)

        self.task_service = task_service
        self.category_service = category_service
        self.category_map = {}

        ttk.Label(
            self,
            text="Υποχρεώσεις / Επιθυμίες",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Τύπος:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.task_type_combo = ttk.Combobox(
            self,
            values=["obligation", "wish"],
            state="readonly"
        )
        self.task_type_combo.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.task_type_combo.current(0)

        ttk.Label(self, text="Τίτλος:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.title_entry = ttk.Entry(self)
        self.title_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self, text="Ποσό (€):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(self)
        self.amount_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self, text="Κατηγορία:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.category_combo = ttk.Combobox(self, state="readonly")
        self.category_combo.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self, text="Ημ/νία λήξης (YYYY-MM-DD):").grid(
            row=5, column=0, padx=10, pady=5, sticky="w"
        )
        self.due_date_entry = ttk.Entry(self)
        self.due_date_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(self, text="Προτεραιότητα:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.priority_combo = ttk.Combobox(
            self,
            values=["1", "2", "3"],
            state="readonly"
        )
        self.priority_combo.grid(row=6, column=1, padx=10, pady=5, sticky="ew")
        self.priority_combo.current(1)

        ttk.Label(self, text="Σημειώσεις:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.notes_entry = ttk.Entry(self)
        self.notes_entry.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

        ttk.Button(
            self,
            text="Προσθήκη",
            command=self.create_task
        ).grid(row=8, column=1, padx=10, pady=10, sticky="e")

        ttk.Button(
            self,
            text="Ολοκληρώθηκε",
            command=self.mark_selected_done
        ).grid(row=9, column=0, padx=10, pady=5, sticky="w")

        ttk.Button(
            self,
            text="Διαγραφή",
            command=self.delete_selected_task
        ).grid(row=9, column=1, padx=10, pady=5, sticky="e")

        self.tasks_table = ttk.Treeview(
            self,
            columns=("id", "type", "title", "amount", "category", "due", "priority", "status"),
            show="headings",
            height=10
        )

        self.tasks_table.heading("id", text="ID")
        self.tasks_table.heading("type", text="Τύπος")
        self.tasks_table.heading("title", text="Τίτλος")
        self.tasks_table.heading("amount", text="Ποσό")
        self.tasks_table.heading("category", text="Κατηγορία")
        self.tasks_table.heading("due", text="Λήξη")
        self.tasks_table.heading("priority", text="Προτερ.")
        self.tasks_table.heading("status", text="Status")

        self.tasks_table.grid(row=10, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.columnconfigure(1, weight=1)
        self.rowconfigure(10, weight=1)

        self.load_categories()
        self.load_tasks()

    def load_categories(self):
        try:
            categories = self.category_service.get_all_categories(active_only=True)
            self.category_map = {"Χωρίς κατηγορία": None}

            for category in categories:
                self.category_map[category.name] = category.id

            self.category_combo["values"] = list(self.category_map.keys())
            self.category_combo.current(0)

        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def create_task(self):
        task_type = self.task_type_combo.get()
        title = self.title_entry.get().strip()
        amount = self.amount_entry.get().strip()
        category_name = self.category_combo.get()
        due_date = self.due_date_entry.get().strip()
        priority = self.priority_combo.get()
        notes = self.notes_entry.get().strip()

        amount = None if amount == "" else amount
        due_date = None if due_date == "" else due_date
        notes = None if notes == "" else notes
        category_id = self.category_map.get(category_name)

        try:
            self.task_service.create_task(
                task_type=task_type,
                title=title,
                amount=amount,
                category_id=category_id,
                due_date=due_date,
                priority=priority,
                notify_days_before=3,
                notes=notes,
            )

            messagebox.showinfo("Επιτυχία", "Το task προστέθηκε.")
            self.clear_form()
            self.load_tasks()

        except ValidationError as e:
            messagebox.showerror("Σφάλμα εγκυρότητας", str(e))
        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def load_tasks(self):
        for item in self.tasks_table.get_children():
            self.tasks_table.delete(item)

        try:
            tasks = self.task_service.list_tasks()

            for task in tasks:
                amount = "" if task.amount is None else "{:.2f}".format(task.amount)

                self.tasks_table.insert(
                    "",
                    "end",
                    values=(
                        task.id,
                        task.task_type,
                        task.title,
                        amount,
                        task.category_name if task.category_name else "",
                        task.due_date if task.due_date else "",
                        task.priority,
                        task.status,
                    )
                )

        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def get_selected_task_id(self):
        selected = self.tasks_table.selection()

        if not selected:
            messagebox.showwarning("Προσοχή", "Επίλεξε πρώτα ένα task.")
            return None

        values = self.tasks_table.item(selected[0], "values")
        return int(values[0])

    def mark_selected_done(self):
        task_id = self.get_selected_task_id()
        if task_id is None:
            return

        try:
            self.task_service.mark_done(task_id)
            messagebox.showinfo("Επιτυχία", "Το task σημειώθηκε ως ολοκληρωμένο.")
            self.load_tasks()

        except NotFoundError as e:
            messagebox.showerror("Δεν βρέθηκε", str(e))
        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def delete_selected_task(self):
        task_id = self.get_selected_task_id()
        if task_id is None:
            return

        try:
            self.task_service.delete_task(task_id)
            messagebox.showinfo("Επιτυχία", "Το task διαγράφηκε.")
            self.load_tasks()

        except NotFoundError as e:
            messagebox.showerror("Δεν βρέθηκε", str(e))
        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))

    def clear_form(self):
        self.task_type_combo.current(0)
        self.title_entry.delete(0, "end")
        self.amount_entry.delete(0, "end")
        self.category_combo.current(0)
        self.due_date_entry.delete(0, "end")
        self.priority_combo.current(1)
        self.notes_entry.delete(0, "end")
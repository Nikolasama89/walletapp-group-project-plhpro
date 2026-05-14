import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from backend import (
    Database,
    CategoryService,
    TransactionService,
    TaskService,
    StatsService,
    BudgetService,
    NotificationService,
)


class WalletApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Wallet App")
        self.geometry("1150x740")
        self.minsize(1000, 650)

        self.db = Database()
        self.category_service = CategoryService(self.db)
        self.transaction_service = TransactionService(self.db)
        self.task_service = TaskService(self.db)
        self.stats_service = StatsService(self.db)
        self.budget_service = BudgetService(self.db)
        self.notification_service = NotificationService(self.db)

        self.categories = []

        self.create_widgets()
        self.refresh_all()

    # --------------------------------------------------
    # Main UI
    # --------------------------------------------------

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.dashboard_tab = ttk.Frame(self.notebook)
        self.transactions_tab = ttk.Frame(self.notebook)
        self.tasks_tab = ttk.Frame(self.notebook)
        self.categories_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.notebook.add(self.tasks_tab, text="Tasks")
        self.notebook.add(self.categories_tab, text="Categories")

        self.build_dashboard_tab()
        self.build_transactions_tab()
        self.build_tasks_tab()
        self.build_categories_tab()

    # --------------------------------------------------
    # Dashboard
    # --------------------------------------------------

    def build_dashboard_tab(self):
        top = ttk.Frame(self.dashboard_tab)
        top.pack(fill="x", padx=10, pady=10)

        self.balance_label = ttk.Label(top, text="Balance: -", font=("Arial", 16, "bold"))
        self.balance_label.pack(anchor="w")

        self.income_label = ttk.Label(top, text="Income: -")
        self.income_label.pack(anchor="w", pady=2)

        self.expense_label = ttk.Label(top, text="Expense: -")
        self.expense_label.pack(anchor="w", pady=2)

        ttk.Button(top, text="Refresh", command=self.refresh_all).pack(anchor="w", pady=10)

        charts_frame = ttk.Frame(self.dashboard_tab)
        charts_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.pie_chart_frame = ttk.LabelFrame(charts_frame, text="Expenses by Category")
        self.pie_chart_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.bar_chart_frame = ttk.LabelFrame(charts_frame, text="Income vs Expense")
        self.bar_chart_frame.pack(side="left", fill="both", expand=True, padx=5)

        self.line_chart_frame = ttk.LabelFrame(charts_frame, text="Balance Trend")
        self.line_chart_frame.pack(side="left", fill="both", expand=True, padx=5)

        bottom = ttk.Frame(self.dashboard_tab)
        bottom.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(bottom, text="Notifications", font=("Arial", 12, "bold")).pack(anchor="w")

        self.notifications_box = tk.Text(bottom, height=8, wrap="word")
        self.notifications_box.pack(fill="both", expand=True, pady=5)

    # --------------------------------------------------
    # Transactions
    # --------------------------------------------------

    def build_transactions_tab(self):
        form = ttk.LabelFrame(self.transactions_tab, text="Add Transaction")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Type").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.txn_type_var = tk.StringVar(value="expense")
        ttk.Combobox(
            form,
            textvariable=self.txn_type_var,
            values=["income", "expense"],
            state="readonly",
            width=15,
        ).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Amount").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.txn_amount_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.txn_amount_var, width=15).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Date YYYY-MM-DD").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.txn_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(form, textvariable=self.txn_date_var, width=15).grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(form, text="Category").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.txn_category_var = tk.StringVar()
        self.txn_category_combo = ttk.Combobox(
            form,
            textvariable=self.txn_category_var,
            state="readonly",
            width=25,
        )
        self.txn_category_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        ttk.Label(form, text="Note").grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.txn_note_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.txn_note_var, width=30).grid(row=1, column=4, padx=5, pady=5, sticky="w")

        ttk.Button(form, text="Add", command=self.add_transaction).grid(row=1, column=5, padx=5, pady=5)

        self.txn_type_var.trace_add("write", lambda *_: self.refresh_category_dropdowns())

        columns = ("id", "date", "type", "amount", "category", "note")
        self.transactions_tree = ttk.Treeview(self.transactions_tab, columns=columns, show="headings")

        for col in columns:
            self.transactions_tree.heading(col, text=col.title())
            self.transactions_tree.column(col, width=130)

        self.transactions_tree.pack(fill="both", expand=True, padx=10, pady=10)

        txn_btn_frame = ttk.Frame(self.transactions_tab)
        txn_btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(
            txn_btn_frame,
            text="Delete Selected Transaction",
            command=self.delete_selected_transaction,
        ).pack(side="right")

    def add_transaction(self):
        try:
            category_id = self.get_selected_category_id(self.txn_category_var.get())

            self.transaction_service.create_transaction(
                self.txn_type_var.get(),
                self.txn_amount_var.get(),
                category_id,
                self.txn_date_var.get(),
                self.txn_note_var.get() or None,
            )

            self.txn_amount_var.set("")
            self.txn_note_var.set("")
            self.refresh_all()

        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def delete_selected_transaction(self):
        selected = self.transactions_tree.selection()

        if not selected:
            messagebox.showinfo("Info", "Select a transaction first.")
            return

        txn_id = self.transactions_tree.item(selected[0])["values"][0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete the selected transaction?",
        )

        if not confirm:
            return

        try:
            self.transaction_service.delete_transaction(txn_id)
            self.refresh_all()

        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    # --------------------------------------------------
    # Tasks
    # --------------------------------------------------

    def build_tasks_tab(self):
        form = ttk.LabelFrame(self.tasks_tab, text="Add Task")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Type").grid(row=0, column=0, padx=5, pady=5)
        self.task_type_var = tk.StringVar(value="obligation")
        ttk.Combobox(
            form,
            textvariable=self.task_type_var,
            values=["obligation", "wish"],
            state="readonly",
            width=15,
        ).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Title").grid(row=0, column=2, padx=5, pady=5)
        self.task_title_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.task_title_var, width=25).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Amount").grid(row=0, column=4, padx=5, pady=5)
        self.task_amount_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.task_amount_var, width=12).grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(form, text="Due Date YYYY-MM-DD").grid(row=1, column=0, padx=5, pady=5)
        self.task_due_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.task_due_var, width=15).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Priority").grid(row=1, column=2, padx=5, pady=5)
        self.task_priority_var = tk.StringVar(value="2")
        ttk.Combobox(
            form,
            textvariable=self.task_priority_var,
            values=["1", "2", "3"],
            state="readonly",
            width=8,
        ).grid(row=1, column=3, padx=5, pady=5, sticky="w")

        ttk.Button(form, text="Add", command=self.add_task).grid(row=1, column=5, padx=5, pady=5)

        columns = ("id", "type", "title", "amount", "due_date", "priority", "status")
        self.tasks_tree = ttk.Treeview(self.tasks_tab, columns=columns, show="headings")

        for col in columns:
            self.tasks_tree.heading(col, text=col.title())
            self.tasks_tree.column(col, width=130)

        self.tasks_tree.pack(fill="both", expand=True, padx=10, pady=10)

        task_btn_frame = ttk.Frame(self.tasks_tab)
        task_btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(
            task_btn_frame,
            text="Mark Selected Done",
            command=self.mark_task_done,
        ).pack(side="left", padx=5)

        ttk.Button(
            task_btn_frame,
            text="Delete Selected Task",
            command=self.delete_selected_task,
        ).pack(side="left", padx=5)

    def add_task(self):
        try:
            amount = self.task_amount_var.get().strip() or None
            due_date = self.task_due_var.get().strip() or None

            self.task_service.create_task(
                task_type=self.task_type_var.get(),
                title=self.task_title_var.get(),
                amount=amount,
                due_date=due_date,
                priority=self.task_priority_var.get(),
            )

            self.task_title_var.set("")
            self.task_amount_var.set("")
            self.task_due_var.set("")
            self.refresh_all()

        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def mark_task_done(self):
        selected = self.tasks_tree.selection()

        if not selected:
            messagebox.showinfo("Info", "Select a task first.")
            return

        task_id = self.tasks_tree.item(selected[0])["values"][0]

        try:
            self.task_service.mark_done(task_id)
            self.refresh_all()

        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def delete_selected_task(self):
        selected = self.tasks_tree.selection()

        if not selected:
            messagebox.showinfo("Info", "Select a task first.")
            return

        task_id = self.tasks_tree.item(selected[0])["values"][0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete the selected task?",
        )

        if not confirm:
            return

        try:
            self.task_service.delete_task(task_id)
            self.refresh_all()

        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    # --------------------------------------------------
    # Categories
    # --------------------------------------------------

    def build_categories_tab(self):
        form = ttk.LabelFrame(self.categories_tab, text="Add Category")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Name").grid(row=0, column=0, padx=5, pady=5)
        self.category_name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.category_name_var, width=25).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Type").grid(row=0, column=2, padx=5, pady=5)
        self.category_type_var = tk.StringVar(value="expense")
        ttk.Combobox(
            form,
            textvariable=self.category_type_var,
            values=["income", "expense", "both"],
            state="readonly",
            width=15,
        ).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Budget").grid(row=0, column=4, padx=5, pady=5)
        self.category_budget_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.category_budget_var, width=12).grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(form, text="Add", command=self.add_category).grid(row=0, column=6, padx=5, pady=5)

        columns = ("id", "name", "type", "budget", "active")
        self.categories_tree = ttk.Treeview(self.categories_tab, columns=columns, show="headings")

        for col in columns:
            self.categories_tree.heading(col, text=col.title())
            self.categories_tree.column(col, width=130)

        self.categories_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def add_category(self):
        try:
            budget = self.category_budget_var.get().strip() or None

            self.category_service.create_category(
                self.category_name_var.get(),
                self.category_type_var.get(),
                monthly_budget=budget,
            )

            self.category_name_var.set("")
            self.category_budget_var.set("")
            self.refresh_all()

        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    # --------------------------------------------------
    # Refresh helpers
    # --------------------------------------------------

    def refresh_all(self):
        self.refresh_categories()
        self.refresh_category_dropdowns()
        self.refresh_transactions()
        self.refresh_tasks()
        self.refresh_dashboard()
        self.refresh_charts()

    def refresh_categories(self):
        self.categories = self.category_service.get_all_categories(active_only=True)
        self.categories_tree.delete(*self.categories_tree.get_children())

        for cat in self.categories:
            self.categories_tree.insert(
                "",
                "end",
                values=(
                    cat.id,
                    cat.name,
                    cat.type,
                    cat.monthly_budget if cat.monthly_budget is not None else "",
                    "yes" if cat.is_active else "no",
                ),
            )

    def refresh_category_dropdowns(self):
        txn_type = self.txn_type_var.get() if hasattr(self, "txn_type_var") else "expense"
        allowed = [cat for cat in self.categories if cat.type in (txn_type, "both")]
        values = [f"{cat.id} - {cat.name}" for cat in allowed]

        self.txn_category_combo["values"] = values

        if values and self.txn_category_var.get() not in values:
            self.txn_category_var.set(values[0])

    def refresh_transactions(self):
        self.transactions_tree.delete(*self.transactions_tree.get_children())

        txns = self.transaction_service.list_transactions(limit=100)

        for txn in txns:
            self.transactions_tree.insert(
                "",
                "end",
                values=(
                    txn.id,
                    txn.txn_date,
                    txn.txn_type,
                    txn.amount,
                    txn.category_name or "",
                    txn.note or "",
                ),
            )

    def refresh_tasks(self):
        self.tasks_tree.delete(*self.tasks_tree.get_children())

        tasks = self.task_service.list_tasks()

        for task in tasks:
            self.tasks_tree.insert(
                "",
                "end",
                values=(
                    task.id,
                    task.task_type,
                    task.title,
                    task.amount or "",
                    task.due_date or "",
                    task.priority,
                    task.status,
                ),
            )

    def refresh_dashboard(self):
        today = date.today()

        balance = self.stats_service.get_balance(year=today.year, month=today.month)

        self.income_label.config(text=f"Income: {balance['income']} EUR")
        self.expense_label.config(text=f"Expense: {balance['expense']} EUR")
        self.balance_label.config(text=f"Balance: {balance['balance']} EUR")

        notifications = self.notification_service.get_all_notifications()

        lines = ["Overdue:"]

        for item in notifications["overdue"]:
            lines.append(f"- {item['task'].title}: {item['days_overdue']} days overdue")

        lines.append("")
        lines.append("Upcoming:")

        for item in notifications["upcoming"]:
            lines.append(f"- {item['task'].title}: due in {item['days_remaining']} days")

        notification_text = "\n".join(lines)

        self.notifications_box.delete("1.0", "end")
        self.notifications_box.insert("end", notification_text)

    # --------------------------------------------------
    # Matplotlib charts
    # --------------------------------------------------

    def refresh_charts(self):
        self.clear_chart_frame(self.pie_chart_frame)
        self.clear_chart_frame(self.bar_chart_frame)
        self.clear_chart_frame(self.line_chart_frame)

        today = date.today()

        self.draw_expense_pie_chart(today.year, today.month)
        self.draw_income_expense_bar_chart()
        self.draw_balance_line_chart()

    def draw_expense_pie_chart(self, year, month):
        rows = self.stats_service.get_category_distribution(
            "expense",
            year=year,
            month=month,
        )

        rows = [row for row in rows if row["total"] > 0]

        figure = Figure(figsize=(3.8, 3.2), dpi=100)
        axis = figure.add_subplot(111)

        if rows:
            labels = [row["category_name"] for row in rows]
            values = [row["total"] for row in rows]

            axis.pie(values, labels=labels, autopct="%1.1f%%")
            axis.set_title("Current Month Expenses")

        else:
            axis.text(0.5, 0.5, "No expense data", ha="center", va="center")
            axis.set_axis_off()

        self.embed_chart(figure, self.pie_chart_frame)

    def draw_income_expense_bar_chart(self):
        rows = self.stats_service.compare_months(months_back=6)

        labels = [row["label"] for row in rows]
        income_values = [row["income"] for row in rows]
        expense_values = [row["expense"] for row in rows]

        figure = Figure(figsize=(3.8, 3.2), dpi=100)
        axis = figure.add_subplot(111)

        x_positions = list(range(len(labels)))
        width = 0.35

        axis.bar([x - width / 2 for x in x_positions], income_values, width, label="Income")
        axis.bar([x + width / 2 for x in x_positions], expense_values, width, label="Expense")

        axis.set_title("Income vs Expense")
        axis.set_xticks(x_positions)
        axis.set_xticklabels(labels, rotation=30, ha="right")
        axis.legend()

        self.embed_chart(figure, self.bar_chart_frame)

    def draw_balance_line_chart(self):
        rows = self.stats_service.compare_months(months_back=6)

        labels = [row["label"] for row in rows]
        balances = [row["balance"] for row in rows]

        figure = Figure(figsize=(3.8, 3.2), dpi=100)
        axis = figure.add_subplot(111)

        axis.plot(labels, balances, marker="o")
        axis.set_title("Balance Trend")
        axis.set_xticks(list(range(len(labels))))
        axis.set_xticklabels(labels, rotation=30, ha="right")
        axis.axhline(0, linewidth=1)

        self.embed_chart(figure, self.line_chart_frame)

    def embed_chart(self, figure, parent_frame):
        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def clear_chart_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def get_selected_category_id(self, value):
        if not value:
            return None

        return int(value.split(" - ")[0])


if __name__ == "__main__":
    app = WalletApp()
    app.mainloop()

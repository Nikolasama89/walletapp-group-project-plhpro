from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from services.report_service import (
    get_expenses_by_category,
    get_monthly_summary
)


class ReportsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Title
        ttk.Label(
            self,
            text="Αναφορές & Στατιστικά",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        # Buttons
        ttk.Button(
            self,
            text="Pie Chart Κατανομής Κατηγοριών",
            command=self.show_pie_chart
        ).pack(pady=5)

        ttk.Button(
            self,
            text="Σύγκριση Μηνών (Έσοδα / Έξοδα)",
            command=self.show_bar_chart
        ).pack(pady=5)

        # Area where charts will appear
        self.canvas = None

    def show_pie_chart(self):
        data = get_expenses_by_category()

        categories = [item[0] for item in data]
        values = [item[1] for item in data]

        fig = Figure(figsize=(5, 4))
        ax = fig.add_subplot(111)

        ax.pie(values, labels=categories, autopct="%1.1f%%")
        ax.set_title("Έξοδα ανά κατηγορία")

        self._draw_chart(fig)

    def show_bar_chart(self):
        summary = get_monthly_summary()

        months = list(summary.keys())
        income = [summary[m]["income"] for m in months]
        expenses = [summary[m]["expense"] for m in months]

        fig = Figure(figsize=(5, 4))
        ax = fig.add_subplot(111)

        ax.bar(months, income, label="Έσοδα")
        ax.bar(months, expenses, label="Έξοδα")

        ax.set_title("Σύγκριση Μηνών")
        ax.legend()

        self._draw_chart(fig)

    def _draw_chart(self, fig):
        # If there is already a chart, remove it first
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Create and show new chart
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10)
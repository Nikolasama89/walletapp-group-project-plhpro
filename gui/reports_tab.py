from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ReportsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(self, text="Αναφορές & Στατιστικά", font=("Arial", 12)).pack(pady=10)

        ttk.Button(self, text="Pie Chart Κατηγοριών", command=self.show_pie).pack(pady=5)
        ttk.Button(self, text="Σύγκριση Μηνών", command=self.show_bar).pack(pady=5)

        self.canvas = None

    def show_pie(self):
        labels = ["Τρόφιμα", "Ενοίκιο", "Μεταφορές"]
        values = [300, 600, 150]

        fig = Figure(figsize=(5, 4))
        ax = fig.add_subplot(111)
        ax.pie(values, labels=labels, autopct="%1.1f%%")
        ax.set_title("Έξοδα ανά κατηγορία")

        self.draw(fig)

    def show_bar(self):
        months = ["Ιαν", "Φεβ"]
        income = [1200, 1400]
        expenses = [900, 1000]

        fig = Figure(figsize=(5, 4))
        ax = fig.add_subplot(111)
        ax.bar(months, income, label="Έσοδα")
        ax.bar(months, expenses, label="Έξοδα")
        ax.legend()
        ax.set_title("Σύγκριση Μηνών")

        self.draw(fig)

    def draw(self, fig):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
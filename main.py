import tkinter as tk

from backend.database import Database
from backend.services import CategoryService, TransactionService

from gui.main_window import MainWindow


def main():
    # Δημιουργούμε/αρχικοποιούμε τη βάση δεδομένων
    database = Database()

    # Δημιουργούμε τα πραγματικά backend services
    category_service = CategoryService(database)
    transaction_service = TransactionService(database)

    # Δημιουργούμε το βασικό Tkinter παράθυρο
    root = tk.Tk()

    # Περνάμε τα services στο MainWindow
    app = MainWindow(
        root,
        category_service=category_service,
        transaction_service=transaction_service
    )

    # Ξεκινάει το GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()

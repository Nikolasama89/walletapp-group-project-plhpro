import tkinter as tk
from gui.main_window import MainWindow

def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()

    #Το main.py είναι το σημείο εκκίνησης του GUI. 
    # Δημιουργεί το κύριο παράθυρο της εφαρμογής και αρχικοποιεί την κλάση MainWindow,
    #  η οποία χτίζει την υπόλοιπη διεπαφή.


    #Το GUI υλοποιεί το presentation layer της εφαρμογής.
    #  Είναι υπεύθυνο για την αλληλεπίδραση με τον χρήστη και την παρουσίαση δεδομένων, 
    # ενώ η λογική και η αποθήκευση δεδομένων υλοποιούνται σε άλλο επίπεδο.
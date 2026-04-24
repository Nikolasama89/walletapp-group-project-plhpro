"""Δοκιμή των repositories."""
from backend import (
    Database,
    Category, Transaction, Task,
    CategoryRepository, TransactionRepository, TaskRepository,
)


def main():
    db = Database()

    cat_repo = CategoryRepository(db)
    txn_repo = TransactionRepository(db)
    task_repo = TaskRepository(db)

    # Δοκιμή με Λίστα από κατηγορίες
    print(" Κατηγορίες εσόδων ")
    for cat in cat_repo.get_all(type_filter="income"):
        print(" ", cat)

    print("\n Κατηγορίες εξόδων ")
    for cat in cat_repo.get_all(type_filter="expense"):
        print(" ", cat)

    # Δοκιμή για νέα κατηγορία
    print("\n Δημιουργία νέας κατηγορίας ")
    new_cat = Category(name="Γυμναστήριο", type="expense", monthly_budget=50.0)
    new_id = cat_repo.create(new_cat)
    print(" Created with id:", new_id)
    print(" ", cat_repo.get_by_id(new_id))

    # Δοκιμή για νέα συναλλαγή
    print("\nΔημιουργία συναλλαγής ")
    # Βρες id της κατηγορίας "Τρόφιμα"
    food_cat = cat_repo.get_by_name("Τρόφιμα")
    txn = Transaction(
        txn_type="expense",
        amount=35.50,
        txn_date="2026-04-25",
        category_id=food_cat.id,
        note="Σούπερ μάρκετ",
    )
    txn_id = txn_repo.create(txn)
    print("Created with id: ", txn_id)
    print(" ", txn_repo.get_by_id(txn_id))

    # Δημιουργία νέου task
    print("\nΔημιουργία task")
    rent_cat = cat_repo.get_by_name("Ενοίκιο")
    task = Task(
        task_type="obligation",
        title="Πληρωμή ενοίκιο Μαΐου",
        amount=400.0,
        category_id=rent_cat.id if rent_cat else None,
        due_date="2026-05-05",
        priority=1,
    )
    task_id = task_repo.create(task)
    print(" Created with id:", task_id)
    print(" ", task_repo.get_by_id(task_id))

    # Aggregates
    print("\nΣύνολα Απριλίου 2026")
    total_income = txn_repo.sum_by_type("income", year=2026, month=4)
    total_expense = txn_repo.sum_by_type("expense", year=2026, month=4)
    print("  Έσοδα:", total_income)
    print("  Έξοδα:", total_expense)
    print("  Υπόλοιπο:", total_income - total_expense)

    # Κατανομή εξόδων
    print("\nΈξοδα ανά κατηγορία (Απρίλιος) ")
    for row in txn_repo.sum_by_category("expense", year=2026, month=4):
        print("  {}: {:.2f}€".format(row["category_name"], row["total"]))

    # Lista tasks
    print("\nΑνοιχτά tasks ταξινομημένα ανά due_date ")
    for t in task_repo.list_tasks(status="open"):
        print(" ", t)


if __name__ == "__main__":
    main()
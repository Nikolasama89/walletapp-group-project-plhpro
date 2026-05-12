from datetime import date, timedelta

from backend import (
    Database,
    CategoryService, TransactionService, TaskService,
    StatsService, BudgetService, NotificationService,
)


def main():
    db = Database()
    category_service = CategoryService(db)
    transaction_service = TransactionService(db)
    task_service = TaskService(db)
    stats_service = StatsService(db)
    budget_service = BudgetService(db)
    notification_service = NotificationService(db)

    today = date.today()
    today_iso = today.strftime("%Y-%m-%d")

    # Δοκιμή για κατηγορίες
    print(" Κατηγορίες ")
    for cat in category_service.get_all_categories():
        print("  -", cat.name, "(" + cat.type + ")")

    # Δοκιμή για τις συναλλαγές
    print("\n Προσθήκη συναλλαγών ")
    salary = [c for c in category_service.get_all_categories(type_filter="income")
              if c.name == "Μισθός"][0]
    food = [c for c in category_service.get_all_categories(type_filter="expense")
            if c.name == "Τρόφιμα"][0]
    rent = [c for c in category_service.get_all_categories(type_filter="expense")
            if c.name == "Ενοίκιο"][0]

    transaction_service.add_income(amount=1500, category_id=salary.id, txn_date=today_iso,
                       note="Μισθός")
    transaction_service.add_expense(amount=450, category_id=rent.id, txn_date=today_iso,
                        note="Ενοίκιο")
    transaction_service.add_expense(amount=120, category_id=food.id, txn_date=today_iso)
    transaction_service.add_expense(amount=85, category_id=food.id, txn_date=today_iso)

    print("  Προστέθηκαν 4 συναλλαγές")

    # Δοκιμή για tasks
    print("\n Προσθήκη tasks ")
    task_service.create_task(
        task_type="obligation", title="Πληρωμή ΔΕΗ",
        amount=85, due_date=(today + timedelta(days=2)).strftime("%Y-%m-%d"),
        priority=1,
    )
    task_service.create_task(
        task_type="obligation", title="Ληγμένη υποχρέωση",
        due_date=(today - timedelta(days=3)).strftime("%Y-%m-%d"),
    )
    task_service.create_task(
        task_type="wish", title="Αγορά laptop", amount=1200,
    )
    print("  Προστέθηκαν 3 tasks")

    # Δοκιμή για τα stats
    print("\n Ισοζύγιο τρέχοντος μήνα ")
    balance = stats_service.get_balance(year=today.year, month=today.month)
    print("  Έσοδα:   ", balance["income"], "€")
    print("  Έξοδα:   ", balance["expense"], "€")
    print("  Υπόλοιπο:", balance["balance"], "€")

    print("\n Κατανομή εξόδων ανά κατηγορία ")
    for row in stats_service.get_category_distribution(
            "expense", year=today.year, month=today.month):
        print("  -", row["category_name"], ":", row["total"], "€",
              "(" + str(row["percentage"]) + "%)")

    # Δοκιμή για το budget
    print("\n Budget warnings ")
    category_service.set_budget(food.id, 150)  # έχει 205 → exceeded
    warnings = budget_service.get_warnings(year=today.year, month=today.month)
    for w in warnings:
        print("  -", w["category_name"], "(" + w["status"] + "):",
              w["spent"], "/", w["budget"], "€")

    # Δοκιμή για notifications
    print("\n Ειδοποιήσεις ")
    notifications = notification_service.get_all_notifications()
    print("  Επερχόμενα:", len(notifications["upcoming"]))
    for n in notifications["upcoming"]:
        print("    -", n["task"].title, "(σε", n["days_remaining"], "μέρες)")
    print("  Ληγμένα:", len(notifications["overdue"]))
    for n in notifications["overdue"]:
        print("    -", n["task"].title, "(πριν", n["days_overdue"], "μέρες)")


if __name__ == "__main__":
    main()

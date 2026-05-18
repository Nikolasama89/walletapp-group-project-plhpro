from tkinter import ttk, messagebox


class NotificationsTab(ttk.Frame):
    def __init__(self, parent, notification_service):
        super().__init__(parent)

        self.notification_service = notification_service

        ttk.Label(
            self,
            text="Ειδοποιήσεις",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        ttk.Button(
            self,
            text="Ανανέωση",
            command=self.load_notifications
        ).pack(pady=5)

        self.count_label = ttk.Label(self, text="Σύνολο ειδοποιήσεων: 0")
        self.count_label.pack(pady=5)

        self.notifications_table = ttk.Treeview(
            self,
            columns=("kind", "title", "due", "days", "urgency"),
            show="headings",
            height=12
        )

        self.notifications_table.heading("kind", text="Είδος")
        self.notifications_table.heading("title", text="Τίτλος")
        self.notifications_table.heading("due", text="Λήξη")
        self.notifications_table.heading("days", text="Ημέρες")
        self.notifications_table.heading("urgency", text="Urgency")

        self.notifications_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_notifications()

    def load_notifications(self):
        for item in self.notifications_table.get_children():
            self.notifications_table.delete(item)

        try:
            data = self.notification_service.get_all_notifications()

            self.count_label.config(
                text="Σύνολο ειδοποιήσεων: {}".format(data["total_count"])
            )

            for item in data["overdue"]:
                task = item["task"]

                self.notifications_table.insert(
                    "",
                    "end",
                    values=(
                        "overdue",
                        task.title,
                        task.due_date,
                        item["days_overdue"],
                        "critical",
                    )
                )

            for item in data["upcoming"]:
                task = item["task"]

                self.notifications_table.insert(
                    "",
                    "end",
                    values=(
                        "upcoming",
                        task.title,
                        task.due_date,
                        item["days_remaining"],
                        item["urgency"],
                    )
                )

        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))
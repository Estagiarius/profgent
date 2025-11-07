import customtkinter as ctk
from app.services import data_service

class ClassSelectionView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="My Classes", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Select a class to view details")
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.populate_class_cards()

    def populate_class_cards(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        classes = data_service.get_all_classes()
        for i, class_ in enumerate(classes):
            card = self.create_class_card(self.scrollable_frame, class_)
            card.grid(row=i, column=0, padx=10, pady=10, sticky="ew")

    def create_class_card(self, parent, class_):
        card = ctk.CTkFrame(parent)
        card.grid_columnconfigure(0, weight=1)

        # Class Name
        class_name_label = ctk.CTkLabel(card, text=class_.name, font=ctk.CTkFont(size=16, weight="bold"))
        class_name_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        # Course Name
        course_name_label = ctk.CTkLabel(card, text=class_.course.course_name, font=ctk.CTkFont(size=12))
        course_name_label.grid(row=1, column=0, padx=15, pady=0, sticky="w")

        # Number of Students
        student_count = len(class_.enrollments)
        student_count_label = ctk.CTkLabel(card, text=f"{student_count} students enrolled", font=ctk.CTkFont(size=10))
        student_count_label.grid(row=2, column=0, padx=15, pady=(5, 10), sticky="w")

        # Details Button
        details_button = ctk.CTkButton(card, text="View Details", command=lambda c=class_.id: self.view_class_details(c))
        details_button.grid(row=0, column=1, rowspan=3, padx=15, pady=15, sticky="e")

        return card

    def view_class_details(self, class_id):
        self.main_app.show_view("class_detail", class_id=class_id)

    def on_show(self, **kwargs):
        self.populate_class_cards()

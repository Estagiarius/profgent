import customtkinter as ctk
from app.services import data_service
from app.ui.views.add_dialog import AddDialog
from app.ui.views.edit_dialog import EditDialog
from customtkinter import CTkInputDialog

class ClassSelectionView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Minhas Turmas", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.add_class_button = ctk.CTkButton(self, text="Adicionar Nova Turma", command=self.add_class_popup)
        self.add_class_button.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="e")

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Selecione uma turma para ver os detalhes")
        self.scrollable_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.populate_class_cards()

    def populate_class_cards(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        classes_data = data_service.get_all_classes()
        for i, class_data in enumerate(classes_data):
            card = self.create_class_card(self.scrollable_frame, class_data)
            card.grid(row=i, column=0, padx=10, pady=10, sticky="ew")

    def create_class_card(self, parent, class_data):
        card = ctk.CTkFrame(parent)
        card.grid_columnconfigure(0, weight=1)

        class_name_label = ctk.CTkLabel(card, text=class_data["name"], font=ctk.CTkFont(size=16, weight="bold"))
        class_name_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        course_name_label = ctk.CTkLabel(card, text=class_data["course_name"], font=ctk.CTkFont(size=12))
        course_name_label.grid(row=1, column=0, padx=15, pady=0, sticky="w")

        student_count_label = ctk.CTkLabel(card, text=f"{class_data['student_count']} alunos matriculados", font=ctk.CTkFont(size=10))
        student_count_label.grid(row=2, column=0, padx=15, pady=(5, 10), sticky="w")

        actions_frame = ctk.CTkFrame(card)
        actions_frame.grid(row=0, column=1, rowspan=3, padx=15, pady=15, sticky="e")

        details_button = ctk.CTkButton(actions_frame, text="Ver Detalhes", command=lambda c=class_data["id"]: self.view_class_details(c))
        details_button.pack(side="top", fill="x", padx=5, pady=5)

        edit_button = ctk.CTkButton(actions_frame, text="Editar", command=lambda c=class_data: self.edit_class_popup(c))
        edit_button.pack(side="top", fill="x", padx=5, pady=5)

        delete_button = ctk.CTkButton(actions_frame, text="Excluir", fg_color="red", command=lambda c_id=class_data["id"]: self.delete_class_action(c_id))
        delete_button.pack(side="top", fill="x", padx=5, pady=5)

        return card

    def delete_class_action(self, class_id):
        dialog = CTkInputDialog(text="Esta é uma ação destrutiva. Todas as matrículas e notas relacionadas a esta turma serão perdidas.\nDigite 'DELETE' para confirmar a exclusão:", title="Confirmar Exclusão")
        user_input = dialog.get_input()
        if user_input == "DELETE":
            data_service.delete_class(class_id)
            self.populate_class_cards()

    def view_class_details(self, class_id):
        self.main_app.show_view("class_detail", class_id=class_id)

    def edit_class_popup(self, class_data):
        def save_callback(class_id, data):
            new_name = data.get("name")
            if new_name:
                data_service.update_class(class_id, new_name)
                self.populate_class_cards()

        fields = {"name": "Nome da Turma"}
        initial_data = {"id": class_data["id"], "name": class_data["name"]}

        EditDialog(self, "Editar Turma", fields, initial_data, save_callback)

    def add_class_popup(self):
        courses_data = data_service.get_all_courses()
        if not courses_data:
            messagebox.showerror("Erro", "Nenhum curso disponível. Adicione um curso primeiro na tela de Gestão de Dados.")
            return

        course_names = [c["course_name"] for c in courses_data]

        def save_callback(data):
            class_name = data.get("name")
            selected_course_name = data.get("course")

            if not class_name or not selected_course_name:
                messagebox.showerror("Erro", "O nome da turma e o curso são obrigatórios.")
                return

            selected_course = next((c for c in courses_data if c["course_name"] == selected_course_name), None)

            if selected_course:
                data_service.create_class(name=class_name, course_id=selected_course["id"])
                self.populate_class_cards()

        fields = {"name": "Nome da Turma"}
        dropdowns = {"course": ("Curso", course_names)}

        AddDialog(self, "Adicionar Nova Turma", fields=fields, dropdowns=dropdowns, save_callback=save_callback)

    def on_show(self, **kwargs):
        self.populate_class_cards()

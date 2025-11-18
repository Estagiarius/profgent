# Importa a biblioteca 'customtkinter' para os componentes da interface.
import customtkinter as ctk
# Importa o serviço de dados para acessar as informações do banco.
from app.services import data_service
# Importa as janelas de diálogo personalizadas para adicionar e editar.
from app.ui.views.add_dialog import AddDialog
from app.ui.views.edit_dialog import EditDialog
# Importa a janela de diálogo de entrada de texto padrão do customtkinter.
from customtkinter import CTkInputDialog
# Importa a biblioteca tkinter para exibir caixas de mensagem.
from tkinter import messagebox

# Define a classe para a tela de seleção de turmas.
class ClassSelectionView(ctk.CTkFrame):
    # Método construtor.
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        # Configura o layout de grade da view.
        self.grid_rowconfigure(1, weight=1) # A linha 1 (com a lista) se expande.
        self.grid_columnconfigure(1, weight=1) # A coluna 1 (onde está o botão de adicionar) se expande.

        # Rótulo do título da tela.
        self.title_label = ctk.CTkLabel(self, text="Minhas Turmas", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Botão para abrir o pop-up de adição de nova turma.
        self.add_class_button = ctk.CTkButton(self, text="Adicionar Nova Turma", command=self.add_class_popup)
        self.add_class_button.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="e")

        # Frame com rolagem onde os cards das turmas serão exibidos.
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Selecione uma turma para ver os detalhes")
        self.scrollable_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1) # Permite que os cards se expandam horizontalmente.

        # Chama o método para preencher a lista de turmas ao iniciar.
        self.populate_class_cards()

    # Método para buscar os dados das turmas e criar os cards na tela.
    def populate_class_cards(self):
        # Limpa todos os widgets existentes no frame de rolagem antes de recriá-los.
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Busca todas as turmas do banco de dados através do serviço.
        classes_data = data_service.get_all_classes()
        # Itera sobre os dados de cada turma.
        for i, class_data in enumerate(classes_data):
            # Cria um widget de card para a turma.
            card = self.create_class_card(self.scrollable_frame, class_data)
            # Posiciona o card na grade do frame de rolagem.
            card.grid(row=i, column=0, padx=10, pady=10, sticky="ew")

    # Método que cria um único widget de card para uma turma.
    def create_class_card(self, parent, class_data):
        # O card é um CTkFrame.
        card = ctk.CTkFrame(parent)
        card.grid_columnconfigure(0, weight=1) # A coluna 0 (com as informações) se expande.

        # Rótulo com o nome da turma.
        class_name_label = ctk.CTkLabel(card, text=class_data["name"], font=ctk.CTkFont(size=16, weight="bold"))
        class_name_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        # Rótulo com o nome do curso.
        course_name_label = ctk.CTkLabel(card, text=class_data["course_name"], font=ctk.CTkFont(size=12))
        course_name_label.grid(row=1, column=0, padx=15, pady=0, sticky="w")

        # Rótulo com a contagem de alunos.
        student_count_label = ctk.CTkLabel(card, text=f"{class_data['student_count']} alunos matriculados", font=ctk.CTkFont(size=10))
        student_count_label.grid(row=2, column=0, padx=15, pady=(5, 10), sticky="w")

        # Frame para agrupar os botões de ação (Detalhes, Editar, Excluir).
        actions_frame = ctk.CTkFrame(card)
        actions_frame.grid(row=0, column=1, rowspan=3, padx=15, pady=15, sticky="e")

        # Botão "Ver Detalhes". O lambda é usado para passar o ID da turma para a função.
        details_button = ctk.CTkButton(actions_frame, text="Ver Detalhes", command=lambda c=class_data["id"]: self.view_class_details(c))
        details_button.pack(side="top", fill="x", padx=5, pady=5)

        # Botão "Editar".
        edit_button = ctk.CTkButton(actions_frame, text="Editar", command=lambda c=class_data: self.edit_class_popup(c))
        edit_button.pack(side="top", fill="x", padx=5, pady=5)

        # Botão "Excluir".
        delete_button = ctk.CTkButton(actions_frame, text="Excluir", fg_color="red", command=lambda c_id=class_data["id"]: self.delete_class_action(c_id))
        delete_button.pack(side="top", fill="x", padx=5, pady=5)

        return card

    # Ação de deletar uma turma após confirmação do usuário.
    def delete_class_action(self, class_id):
        # Cria um diálogo de confirmação que exige que o usuário digite 'DELETE'.
        dialog = CTkInputDialog(text="Esta é uma ação destrutiva. Todas as matrículas e notas relacionadas a esta turma serão perdidas.\nDigite 'DELETE' para confirmar a exclusão:", title="Confirmar Exclusão")
        user_input = dialog.get_input()
        # Se o usuário confirmou corretamente.
        if user_input == "DELETE":
            # Chama o serviço para deletar a turma.
            data_service.delete_class(class_id)
            # Atualiza a lista de cards na tela.
            self.populate_class_cards()

    # Navega para a tela de detalhes da turma.
    def view_class_details(self, class_id):
        # Chama o método da aplicação principal para mostrar a view 'class_detail', passando o ID da turma.
        self.main_app.show_view("class_detail", class_id=class_id)

    # Abre o pop-up para editar os dados de uma turma.
    def edit_class_popup(self, class_data):
        # Função de callback que será chamada pelo diálogo ao salvar.
        def save_callback(class_id, data):
            new_name = data.get("name")
            if new_name:
                data_service.update_class(class_id, new_name)
                self.populate_class_cards()

        # Configuração dos campos para o diálogo de edição.
        fields = {"name": "Nome da Turma"}
        initial_data = {"id": class_data["id"], "name": class_data["name"]}
        EditDialog(self, "Editar Turma", fields, initial_data, save_callback)

    # Abre o pop-up para adicionar uma nova turma.
    def add_class_popup(self):
        # Busca os cursos disponíveis para preencher o dropdown.
        courses_data = data_service.get_all_courses()
        # Se não houver cursos, exibe um erro e impede a criação da turma.
        if not courses_data:
            messagebox.showerror("Erro", "Nenhum curso disponível. Adicione um curso primeiro na tela de Gestão de Dados.")
            return

        course_names = [c["course_name"] for c in courses_data]

        # Função de callback para o diálogo de adição.
        def save_callback(data):
            class_name = data.get("name")
            selected_course_name = data.get("course")

            if not class_name or not selected_course_name:
                messagebox.showerror("Erro", "O nome da turma e o curso são obrigatórios.")
                return

            # Encontra o objeto do curso correspondente ao nome selecionado.
            selected_course = next((c for c in courses_data if c["course_name"] == selected_course_name), None)

            if selected_course:
                # Chama o serviço para criar a nova turma.
                data_service.create_class(name=class_name, course_id=selected_course["id"])
                # Atualiza a lista de cards.
                self.populate_class_cards()

        # Configuração dos campos para o diálogo de adição.
        fields = {"name": "Nome da Turma"}
        dropdowns = {"course": ("Curso", course_names)}
        AddDialog(self, "Adicionar Nova Turma", fields=fields, dropdowns=dropdowns, save_callback=save_callback)

    # Método chamado sempre que a view é exibida.
    def on_show(self, **kwargs):
        # Atualiza a lista de turmas para garantir que os dados estejam sempre recentes.
        self.populate_class_cards()

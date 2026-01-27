# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
# Importa a biblioteca 'customtkinter' para os componentes da interface.
import customtkinter as ctk
# Importa funções para salvar e carregar configurações gerais da aplicação.
from app.core.config import save_setting, load_setting
import sys
import os


# Define a classe para a tela de Configurações.
class SettingsView(ctk.CTkFrame):
    """
    Uma classe que representa a interface de configuração.
    Fornece recursos para personalizar a aplicação, como o tema.

    :ivar main_app: Referência para a aplicação principal.
    :ivar feedback_label: Label para exibir mensagens de feedback sobre eventos, como salvamento de configurações.
    :type feedback_label: ctk.CTkLabel
    """
    # Método construtor.
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app

        # Configura o layout de grade da view.
        self.grid_columnconfigure(0, weight=1)

        # --- Aparência e Tema ---
        self.appearance_frame = ctk.CTkFrame(self)
        self.appearance_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(self.appearance_frame, text="Tema da Aplicação").pack(side="left", padx=10, pady=10)

        self.theme_map = {
            "Black & Orange": "app/ui/themes/black_orange.json",
            "Ocean Breeze": "app/ui/themes/ocean_breeze.json",
            "Dracula": "app/ui/themes/dracula.json",
            "Forest Glade": "app/ui/themes/forest_glade.json",
            "Padrão (Azul)": "blue" # Fallback to default
        }
        self.theme_var = ctk.StringVar(value=load_setting("app_theme_name", "Black & Orange"))
        self.theme_menu = ctk.CTkOptionMenu(self.appearance_frame, values=list(self.theme_map.keys()), variable=self.theme_var)
        self.theme_menu.pack(side="left", padx=10, pady=10)

        self.save_theme_button = ctk.CTkButton(self.appearance_frame, text="Salvar Tema", command=self.save_theme_only)
        self.save_theme_button.pack(side="left", padx=5)

        self.restart_button = ctk.CTkButton(self.appearance_frame, text="Salvar e Reiniciar", command=self.save_theme_and_restart, fg_color="#b91c1c", hover_color="#991b1b")
        self.restart_button.pack(side="left", padx=5)

        self.feedback_label = ctk.CTkLabel(self, text=""); self.feedback_label.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

    def save_theme_only(self):
        theme_name = self.theme_var.get()
        theme_path = self.theme_map.get(theme_name)
        if theme_path:
            save_setting("app_theme_name", theme_name)
            save_setting("app_theme_path", theme_path)
            self.feedback_label.configure(text="Tema salvo. Reinicie a aplicação para aplicar todas as mudanças.", text_color="orange")

    def save_theme_and_restart(self):
        self.save_theme_only()
        # Reinicia a aplicação
        self.feedback_label.configure(text="Reiniciando...", text_color="orange")
        self.after(500, lambda: os.execl(sys.executable, sys.executable, *sys.argv))

# Importa a biblioteca 'customtkinter' para os componentes da interface.
import customtkinter as ctk
# Importa tipos para anotações, melhorando a clareza do código.
from typing import Dict, Callable, List, Union, Tuple
from app.ui.views.bncc_selection_dialog import BNCCSelectionDialog

# Define a classe EditDialog, que herda de CTkToplevel para criar uma janela secundária (pop-up).
class EditDialog(ctk.CTkToplevel):
    # O método construtor da janela de diálogo.
    def __init__(self, parent, title: str, fields: Dict[str, str], data: Dict[str, any], save_callback: Callable, dropdowns: Dict[str, Tuple[str, List[str]]] = None):
        # Chama o construtor da classe pai.
        super().__init__(parent)
        self.title(title)
        self.save_callback = save_callback
        self.data = data
        self.entries: Dict[str, Union[ctk.CTkEntry, ctk.CTkOptionMenu]] = {}

        current_row = 0

        # Cria campos de entrada de texto
        for key, label in fields.items():
            ctk.CTkLabel(self, text=label).grid(row=current_row, column=0, padx=10, pady=10, sticky="w")

            if key in ['bncc', 'bncc_expected', 'bncc_codes']:
                frame = ctk.CTkFrame(self, fg_color="transparent")
                frame.grid(row=current_row, column=1, padx=10, pady=10, sticky="ew")
                frame.grid_columnconfigure(0, weight=1)

                entry = ctk.CTkEntry(frame)
                entry.insert(0, str(data.get(key, '')))
                entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

                btn = ctk.CTkButton(frame, text="Selecionar", width=80, command=lambda e=entry: self._open_bncc_selector(e))
                btn.grid(row=0, column=1)

                self.entries[key] = entry
            else:
                entry = ctk.CTkEntry(self)
                entry.insert(0, str(data.get(key, '')))
                entry.grid(row=current_row, column=1, padx=10, pady=10, sticky="ew")
                self.entries[key] = entry

            current_row += 1

        # Cria dropdowns (se houver)
        if dropdowns:
            for key, (label, options) in dropdowns.items():
                ctk.CTkLabel(self, text=label).grid(row=current_row, column=0, padx=10, pady=10, sticky="w")
                dropdown = ctk.CTkOptionMenu(self, values=options)

                # Tenta definir o valor inicial
                initial_value = data.get(key)
                if initial_value and str(initial_value) in options:
                    dropdown.set(str(initial_value))
                elif options:
                    dropdown.set(options[0])

                dropdown.grid(row=current_row, column=1, padx=10, pady=10, sticky="ew")
                self.entries[key] = dropdown
                current_row += 1

        # Cria o botão "Salvar".
        save_button = ctk.CTkButton(self, text="Salvar", command=self.save)
        save_button.grid(row=current_row, column=0, columnspan=2, padx=10, pady=20)

    def _open_bncc_selector(self, entry_widget):
        def on_select(codes):
            current_text = entry_widget.get()
            current_codes = [c.strip() for c in current_text.split(',') if c.strip()]
            new_codes = [c for c in codes if c not in current_codes]
            final_list = current_codes + new_codes
            entry_widget.delete(0, "end")
            entry_widget.insert(0, ", ".join(final_list))

        BNCCSelectionDialog(self, on_select)

    # Método chamado quando o botão "Salvar" é clicado.
    def save(self):
        # Cria um dicionário com os dados atualizados, obtendo os valores de cada campo de entrada.
        updated_data = {key: widget.get() for key, widget in self.entries.items()}
        # Chama a função de callback, passando o ID do item original e os dados atualizados.
        self.save_callback(self.data['id'], updated_data)
        # Fecha a janela de diálogo após salvar.
        self.destroy()

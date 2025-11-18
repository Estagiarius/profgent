# Importa a biblioteca 'customtkinter' para os componentes da interface.
import customtkinter as ctk
# Importa tipos para anotações, melhorando a clareza do código.
from typing import Dict, Callable

# Define a classe EditDialog, que herda de CTkToplevel para criar uma janela secundária (pop-up).
class EditDialog(ctk.CTkToplevel):
    # O método construtor da janela de diálogo.
    def __init__(self, parent, title: str, fields: Dict[str, str], data: Dict[str, any], save_callback: Callable):
        # Chama o construtor da classe pai.
        super().__init__(parent)
        # Define o título da janela.
        self.title(title)
        # Armazena a função de callback que será chamada ao salvar.
        self.save_callback = save_callback
        # Armazena os dados iniciais do item que está sendo editado (incluindo o ID).
        self.data = data
        # Cria um dicionário para armazenar os widgets de entrada de texto.
        self.entries: Dict[str, ctk.CTkEntry] = {}

        # Itera sobre os campos que devem ser criados no diálogo.
        # `enumerate` fornece um contador 'i' para o índice da linha na grade.
        for i, (key, label) in enumerate(fields.items()):
            # Cria um rótulo (label) para o campo.
            ctk.CTkLabel(self, text=label).grid(row=i, column=0, padx=10, pady=10, sticky="w")
            # Cria o campo de entrada (entry).
            entry = ctk.CTkEntry(self)
            # **Diferença principal do AddDialog**: Preenche o campo com o valor existente.
            # `data.get(key, '')` busca o valor no dicionário de dados; se não encontrar, usa uma string vazia.
            entry.insert(0, str(data.get(key, '')))
            # Posiciona o campo de entrada na grade.
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            # Armazena o widget no dicionário de entradas para referência posterior.
            self.entries[key] = entry

        # Cria o botão "Salvar".
        save_button = ctk.CTkButton(self, text="Salvar", command=self.save)
        # Posiciona o botão abaixo dos campos de entrada, ocupando duas colunas.
        save_button.grid(row=len(fields), column=0, columnspan=2, padx=10, pady=20)

    # Método chamado quando o botão "Salvar" é clicado.
    def save(self):
        # Cria um dicionário com os dados atualizados, obtendo os valores de cada campo de entrada.
        updated_data = {key: entry.get() for key, entry in self.entries.items()}
        # Chama a função de callback, passando o ID do item original e os dados atualizados.
        self.save_callback(self.data['id'], updated_data)
        # Fecha a janela de diálogo após salvar.
        self.destroy()

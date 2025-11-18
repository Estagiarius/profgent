# Importa a biblioteca 'customtkinter' para criar os componentes da interface.
import customtkinter as ctk
# Importa tipos para anotações, melhorando a clareza e a robustez do código.
from typing import Dict, Callable, List

# Define a classe AddDialog, que herda de CTkToplevel para criar uma janela secundária (pop-up).
class AddDialog(ctk.CTkToplevel):
    # O método construtor da janela de diálogo.
    def __init__(self, parent, title: str, fields: Dict[str, str], dropdowns: Dict[str, List[str]] = None, save_callback: Callable = None):
        # Chama o construtor da classe pai, passando a janela principal como 'parent'.
        super().__init__(parent)
        # Define o título da janela.
        self.title(title)
        # Armazena a função de callback que será chamada ao salvar.
        self.save_callback = save_callback
        # Cria um dicionário para armazenar os widgets de entrada (campos de texto, menus dropdown).
        self.entries: Dict[str, ctk.CTkEntry | ctk.CTkOptionMenu] = {}

        # Inicializa um contador para o índice da linha no layout de grade.
        row_index = 0

        # Cria os menus dropdown primeiro, se houver algum especificado.
        if dropdowns:
            # Itera sobre os itens do dicionário de dropdowns.
            for key, (label, options) in dropdowns.items():
                # Cria um rótulo (label) para o campo.
                ctk.CTkLabel(self, text=label).grid(row=row_index, column=0, padx=10, pady=10, sticky="w")
                # Cria o menu dropdown com as opções fornecidas.
                dropdown = ctk.CTkOptionMenu(self, values=options)
                # Posiciona o dropdown na grade. 'sticky="ew"' faz com que ele se expanda horizontalmente.
                dropdown.grid(row=row_index, column=1, padx=10, pady=10, sticky="ew")
                # Armazena o widget no dicionário de entradas, usando a 'key' como identificador.
                self.entries[key] = dropdown
                # Incrementa o índice da linha para o próximo widget.
                row_index += 1

        # Cria os campos de entrada de texto.
        for key, label in fields.items():
            # Cria um rótulo para o campo de texto.
            ctk.CTkLabel(self, text=label).grid(row=row_index, column=0, padx=10, pady=10, sticky="w")
            # Cria o campo de entrada (entry).
            entry = ctk.CTkEntry(self)
            # Posiciona o campo na grade.
            entry.grid(row=row_index, column=1, padx=10, pady=10, sticky="ew")
            # Armazena o widget no dicionário de entradas.
            self.entries[key] = entry
            # Incrementa o índice da linha.
            row_index += 1

        # Cria o botão "Salvar" que aciona o método `save`.
        save_button = ctk.CTkButton(self, text="Salvar", command=self.save)
        # Posiciona o botão na grade, fazendo-o ocupar duas colunas ('columnspan=2').
        save_button.grid(row=row_index, column=0, columnspan=2, padx=10, pady=20)

    # Método chamado quando o botão "Salvar" é clicado.
    def save(self):
        # Cria um dicionário 'data' coletando o valor de cada widget de entrada.
        # O método `.get()` é usado para obter o valor de CTkEntry e CTkOptionMenu.
        data = {key: widget.get() for key, widget in self.entries.items()}
        # Se uma função de callback foi fornecida no construtor...
        if self.save_callback:
            # ...chama essa função, passando o dicionário de dados coletados.
            self.save_callback(data)
        # Fecha a janela de diálogo após salvar.
        self.destroy()

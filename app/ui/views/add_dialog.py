import customtkinter as ctk
from typing import Dict, Callable, List

class AddDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, fields: Dict[str, str], dropdowns: Dict[str, List[str]] = None, save_callback: Callable = None):
        super().__init__(parent)
        self.title(title)
        self.save_callback = save_callback
        self.entries: Dict[str, ctk.CTkEntry | ctk.CTkOptionMenu] = {}

        row_index = 0

        # Create dropdowns first, if any
        if dropdowns:
            for key, (label, options) in dropdowns.items():
                ctk.CTkLabel(self, text=label).grid(row=row_index, column=0, padx=10, pady=10, sticky="w")
                dropdown = ctk.CTkOptionMenu(self, values=options)
                dropdown.grid(row=row_index, column=1, padx=10, pady=10, sticky="ew")
                self.entries[key] = dropdown
                row_index += 1

        # Create entry fields
        for key, label in fields.items():
            ctk.CTkLabel(self, text=label).grid(row=row_index, column=0, padx=10, pady=10, sticky="w")
            entry = ctk.CTkEntry(self)
            entry.grid(row=row_index, column=1, padx=10, pady=10, sticky="ew")
            self.entries[key] = entry
            row_index += 1

        save_button = ctk.CTkButton(self, text="Salvar", command=self.save)
        save_button.grid(row=row_index, column=0, columnspan=2, padx=10, pady=20)

    def save(self):
        data = {key: widget.get() for key, widget in self.entries.items()}
        if self.save_callback:
            self.save_callback(data)
        self.destroy()

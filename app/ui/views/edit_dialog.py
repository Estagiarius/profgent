import customtkinter as ctk
from typing import Dict, Callable

class EditDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, fields: Dict[str, str], data: Dict[str, any], save_callback: Callable):
        super().__init__(parent)
        self.title(title)
        self.save_callback = save_callback
        self.data = data
        self.entries: Dict[str, ctk.CTkEntry] = {}

        for i, (key, label) in enumerate(fields.items()):
            ctk.CTkLabel(self, text=label).grid(row=i, column=0, padx=10, pady=10, sticky="w")
            entry = ctk.CTkEntry(self)
            entry.insert(0, str(data.get(key, '')))
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            self.entries[key] = entry

        save_button = ctk.CTkButton(self, text="Save", command=self.save)
        save_button.grid(row=len(fields), column=0, columnspan=2, padx=10, pady=20)

    def save(self):
        updated_data = {key: entry.get() for key, entry in self.entries.items()}
        self.save_callback(self.data['id'], updated_data)
        self.destroy()

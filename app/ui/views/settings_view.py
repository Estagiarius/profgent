import customtkinter as ctk

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.label = ctk.CTkLabel(self, text="Settings View")
        self.label.pack(pady=20, padx=20)

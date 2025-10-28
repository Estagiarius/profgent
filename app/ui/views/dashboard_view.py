import customtkinter as ctk

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.label = ctk.CTkLabel(self, text="Dashboard View")
        self.label.pack(pady=20, padx=20)

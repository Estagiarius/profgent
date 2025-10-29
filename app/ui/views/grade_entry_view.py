import customtkinter as ctk

class GradeEntryView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.label = ctk.CTkLabel(self, text="Grade Entry View")
        self.label.pack(pady=20, padx=20)

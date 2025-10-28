import customtkinter as ctk
from app.core.security.credentials import save_api_key

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # API Key Entry
        self.api_key_frame = ctk.CTkFrame(self)
        self.api_key_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.api_key_frame.grid_columnconfigure(1, weight=1)

        self.openai_label = ctk.CTkLabel(self.api_key_frame, text="OpenAI API Key")
        self.openai_label.grid(row=0, column=0, padx=10, pady=10)

        self.openai_entry = ctk.CTkEntry(self.api_key_frame, placeholder_text="Enter your OpenAI API key")
        self.openai_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Save Button
        self.save_button = ctk.CTkButton(self, text="Save Credentials", command=self.save_credentials)
        self.save_button.grid(row=2, column=0, padx=20, pady=20, sticky="e")

        # Feedback Label
        self.feedback_label = ctk.CTkLabel(self, text="")
        self.feedback_label.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")


    def save_credentials(self):
        api_key = self.openai_entry.get()
        if api_key:
            save_api_key("OpenAI", api_key)
            self.feedback_label.configure(text="OpenAI API key saved successfully!", text_color="green")
        else:
            self.feedback_label.configure(text="Please enter an API key.", text_color="red")

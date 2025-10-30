import customtkinter as ctk
from app.core.security.credentials import save_api_key
from app.core.config import save_setting, load_setting

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # --- LLM Provider Selection ---
        self.provider_frame = ctk.CTkFrame(self)
        self.provider_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.provider_label = ctk.CTkLabel(self.provider_frame, text="Active AI Provider")
        self.provider_label.pack(side="left", padx=10, pady=10)

        self.provider_var = ctk.StringVar(value=load_setting("active_provider", "OpenAI"))
        self.provider_menu = ctk.CTkOptionMenu(self.provider_frame,
                                               values=["OpenAI", "Maritaca", "OpenRouter", "Ollama"],
                                               variable=self.provider_var,
                                               command=self.provider_changed)
        self.provider_menu.pack(side="right", padx=10, pady=10)

        # --- Ollama Server Address ---
        self.ollama_frame = ctk.CTkFrame(self)
        self.ollama_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.ollama_frame.grid_columnconfigure(1, weight=1)

        self.ollama_label = ctk.CTkLabel(self.ollama_frame, text="Ollama Server URL")
        self.ollama_label.grid(row=0, column=0, padx=10, pady=10)

        self.ollama_entry = ctk.CTkEntry(self.ollama_frame)
        self.ollama_entry.insert(0, load_setting("ollama_url", "http://localhost:11434/v1"))
        self.ollama_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # --- API Key Entries ---
        self.openai_frame = ctk.CTkFrame(self)
        self.openai_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.openai_frame.grid_columnconfigure(1, weight=1)
        self.openai_label = ctk.CTkLabel(self.openai_frame, text="OpenAI API Key")
        self.openai_label.grid(row=0, column=0, padx=10, pady=10)
        self.openai_entry = ctk.CTkEntry(self.openai_frame, placeholder_text="Enter your OpenAI API key")
        self.openai_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.maritaca_frame = ctk.CTkFrame(self)
        self.maritaca_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.maritaca_frame.grid_columnconfigure(1, weight=1)
        self.maritaca_label = ctk.CTkLabel(self.maritaca_frame, text="Maritaca API Key")
        self.maritaca_label.grid(row=0, column=0, padx=10, pady=10)
        self.maritaca_entry = ctk.CTkEntry(self.maritaca_frame, placeholder_text="Enter your Maritaca API key")
        self.maritaca_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.openrouter_frame = ctk.CTkFrame(self)
        self.openrouter_frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.openrouter_frame.grid_columnconfigure(1, weight=1)
        self.openrouter_label = ctk.CTkLabel(self.openrouter_frame, text="OpenRouter API Key")
        self.openrouter_label.grid(row=0, column=0, padx=10, pady=10)
        self.openrouter_entry = ctk.CTkEntry(self.openrouter_frame, placeholder_text="Enter your OpenRouter API key")
        self.openrouter_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # --- Save Button ---
        self.save_button = ctk.CTkButton(self, text="Save Settings", command=self.save_settings)
        self.save_button.grid(row=6, column=0, padx=20, pady=20, sticky="e")

        # --- Feedback Label ---
        self.feedback_label = ctk.CTkLabel(self, text="")
        self.feedback_label.grid(row=7, column=0, padx=20, pady=(0, 10), sticky="ew")

    def provider_changed(self, choice):
        save_setting("active_provider", choice)
        self.feedback_label.configure(text=f"{choice} is now the active provider.", text_color="green")

    def save_settings(self):
        # Save Ollama URL
        ollama_url = self.ollama_entry.get()
        save_setting("ollama_url", ollama_url)

        # Save API keys
        keys_to_save = {
            "OpenAI": self.openai_entry.get(),
            "Maritaca": self.maritaca_entry.get(),
            "OpenRouter": self.openrouter_entry.get()
        }

        saved_keys = []
        for service, key in keys_to_save.items():
            if key:
                save_api_key(service, key)
                saved_keys.append(service)

        feedback_messages = []
        if ollama_url:
            feedback_messages.append("Ollama URL saved")
        if saved_keys:
            feedback_messages.append(f"{' & '.join(saved_keys)} key(s) saved")

        if feedback_messages:
            self.feedback_label.configure(text=f"Successfully saved: {', '.join(feedback_messages)}.", text_color="green")
        else:
            self.feedback_label.configure(text="No new settings to save.", text_color="orange")

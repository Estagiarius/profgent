import customtkinter as ctk
from app.core.security.credentials import get_api_key, save_api_key
from app.core.config import save_setting, load_setting
from app.core.llm.openai_provider import OpenAIProvider
from app.core.llm.maritaca_provider import MaritacaProvider
from app.core.llm.open_router_provider import OpenRouterProvider
from app.core.llm.ollama_provider import OllamaProvider
from app.utils.async_utils import run_async_task

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.grid_columnconfigure(0, weight=1)

        # --- Provider Selection ---
        self.provider_frame = ctk.CTkFrame(self)
        self.provider_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(self.provider_frame, text="Active AI Provider").pack(side="left", padx=10, pady=10)
        self.provider_var = ctk.StringVar(value=load_setting("active_provider", "OpenAI"))
        self.provider_menu = ctk.CTkOptionMenu(self.provider_frame, values=["OpenAI", "Maritaca", "OpenRouter", "Ollama"], variable=self.provider_var, command=self.provider_changed)
        self.provider_menu.pack(side="right", padx=10, pady=10)

        # --- Model Selection ---
        self.model_frame = ctk.CTkFrame(self)
        self.model_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.model_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.model_frame, text="Select/Enter Model").grid(row=0, column=0, padx=10, pady=10)
        self.model_var = ctk.StringVar()
        self.model_menu = ctk.CTkOptionMenu(self.model_frame, variable=self.model_var, values=["(Refresh to load)"], command=self.model_changed)
        self.model_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.model_entry = ctk.CTkEntry(self.model_frame, placeholder_text="Or enter model name manually")
        self.model_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.refresh_button = ctk.CTkButton(self.model_frame, text="Refresh List", command=self.refresh_models)
        self.refresh_button.grid(row=0, column=2, padx=10, pady=10)

        # Other settings frames...

        self.bind("<Visibility>", lambda event: self.refresh_models())
        self.provider_changed(self.provider_var.get()) # Initial setup

    def provider_changed(self, choice):
        save_setting("active_provider", choice)
        self.feedback_label.configure(text=f"{choice} is now active.")

        # Show/hide Ollama-specific manual entry
        is_ollama = choice == "Ollama"
        if is_ollama:
            self.model_entry.grid()
        else:
            self.model_entry.grid_remove()

        self.refresh_models()

    def model_changed(self, choice):
        # When a model is selected from the dropdown, also update the manual entry field
        if self.provider_var.get() == "Ollama":
            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, choice)
        self.save_model_setting()

    def save_model_setting(self):
        provider = self.provider_var.get().lower()
        # For Ollama, prioritize the manual entry. For others, use the dropdown.
        model_to_save = self.model_entry.get() if provider == "ollama" and self.model_entry.get() else self.model_var.get()
        if "(No models" not in model_to_save and "Loading..." not in model_to_save:
            save_setting(f"{provider}_model", model_to_save)
            self.feedback_label.configure(text=f"Set {provider} model to: {model_to_save}", text_color="green")

    def save_settings(self):
        self.save_model_setting()
        # ... (rest of the save_settings logic)

    def refresh_models(self):
        # ... (rest of the refresh_models logic)

    def _load_models_thread(self):
        # ... (rest of _load_models_thread logic)

    def _update_models_ui(self, models):
        provider = self.provider_var.get().lower()
        if models:
            self.model_menu.configure(values=models)
            saved_model = load_setting(f"{provider}_model", models[0])
            self.model_var.set(saved_model if saved_model in models else models[0])
        else:
            self.model_menu.configure(values=["(List failed)"]); self.model_var.set("(List failed)")

        # For Ollama, also set the entry field
        if provider == "ollama":
            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, load_setting(f"{provider}_model", "llama3.1"))

        self.refresh_button.configure(state="normal")

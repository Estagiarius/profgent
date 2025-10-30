import customtkinter as ctk
from app.core.security.credentials import get_api_key, save_api_key
from app.core.config import save_setting, load_setting
from app.core.llm.openai_provider import OpenAIProvider
from app.core.llm.maritaca_provider import MaritacaProvider
from app.core.llm.open_router_provider import OpenRouterProvider
from app.core.llm.ollama_provider import OllamaProvider
import threading
import asyncio

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
        ctk.CTkLabel(self.model_frame, text="Select Model").pack(side="left", padx=10, pady=10)
        self.model_var = ctk.StringVar(value="Loading...")
        self.model_menu = ctk.CTkOptionMenu(self.model_frame, variable=self.model_var, values=["(Refresh to load models)"], command=self.model_changed)
        self.model_menu.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.refresh_button = ctk.CTkButton(self.model_frame, text="Refresh Models", command=self.refresh_models)
        self.refresh_button.pack(side="right", padx=10, pady=10)

        # --- Config Sections ---
        # Ollama
        self.ollama_frame = ctk.CTkFrame(self)
        self.ollama_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(self.ollama_frame, text="Ollama Server URL").pack(side="left", padx=10, pady=10)
        self.ollama_entry = ctk.CTkEntry(self.ollama_frame, width=300)
        self.ollama_entry.insert(0, load_setting("ollama_url", "http://localhost:11434/v1"))
        self.ollama_entry.pack(side="right", fill="x", expand=True, padx=10, pady=10)

        # API Keys
        self.keys_frame = ctk.CTkFrame(self)
        self.keys_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.keys_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.keys_frame, text="OpenAI API Key").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.openai_entry = ctk.CTkEntry(self.keys_frame, placeholder_text="Enter key")
        self.openai_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.keys_frame, text="Maritaca API Key").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.maritaca_entry = ctk.CTkEntry(self.keys_frame, placeholder_text="Enter key")
        self.maritaca_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.keys_frame, text="OpenRouter API Key").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.openrouter_entry = ctk.CTkEntry(self.keys_frame, placeholder_text="Enter key")
        self.openrouter_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # --- Controls ---
        self.save_button = ctk.CTkButton(self, text="Save Settings", command=self.save_settings)
        self.save_button.grid(row=5, column=0, padx=20, pady=20, sticky="e")
        self.feedback_label = ctk.CTkLabel(self, text="")
        self.feedback_label.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.bind("<Visibility>", lambda event: self.refresh_models())

    def provider_changed(self, choice):
        save_setting("active_provider", choice)
        self.feedback_label.configure(text=f"{choice} is now the active provider.", text_color="green")
        self.refresh_models()

    def model_changed(self, choice):
        provider = self.provider_var.get().lower()
        save_setting(f"{provider}_model", choice)
        self.feedback_label.configure(text=f"Set {provider} model to: {choice}", text_color="green")

    def save_settings(self):
        # Save Ollama URL
        save_setting("ollama_url", self.ollama_entry.get())

        # Save API keys
        keys_to_save = {"OpenAI": self.openai_entry.get(), "Maritaca": self.maritaca_entry.get(), "OpenRouter": self.openrouter_entry.get()}
        for service, key in keys_to_save.items():
            if key: save_api_key(service, key)

        self.feedback_label.configure(text="Settings saved successfully!", text_color="green")

    def refresh_models(self):
        self.model_menu.configure(values=["Loading..."])
        self.model_var.set("Loading...")
        self.refresh_button.configure(state="disabled")
        threading.Thread(target=self._load_models_thread).start()

    def _load_models_thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        provider_name = self.provider_var.get()

        # Create a temporary provider instance to list models
        provider = None
        if provider_name == "Ollama":
            provider = OllamaProvider(base_url=self.ollama_entry.get())
        else:
            api_key = get_api_key(provider_name)
            if api_key:
                if provider_name == "OpenAI": provider = OpenAIProvider(api_key)
                elif provider_name == "Maritaca": provider = MaritacaProvider(api_key)
                elif provider_name == "OpenRouter": provider = OpenRouterProvider(api_key)

        models = []
        if provider:
            models = loop.run_until_complete(provider.list_models())

        self.parent.after(0, self._update_models_ui, models)
        loop.close()

    def _update_models_ui(self, models):
        if models:
            self.model_menu.configure(values=models)
            # Try to set the previously saved model for this provider
            provider = self.provider_var.get().lower()
            saved_model = load_setting(f"{provider}_model")
            if saved_model and saved_model in models:
                self.model_var.set(saved_model)
            else:
                self.model_var.set(models[0])
        else:
            self.model_menu.configure(values=["(No models found or API key missing)"])
            self.model_var.set("(No models found or API key missing)")

        self.refresh_button.configure(state="normal")

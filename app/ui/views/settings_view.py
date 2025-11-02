import customtkinter as ctk
from app.core.security.credentials import get_api_key, save_api_key
from app.core.config import save_setting, load_setting
from app.core.llm.openai_provider import OpenAIProvider
from app.core.llm.maritaca_provider import MaritacaProvider
from app.core.llm.open_router_provider import OpenRouterProvider
from app.core.llm.ollama_provider import OllamaProvider
from app.utils.async_utils import run_async_task

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app

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

        # --- Config Sections ---
        self.ollama_frame = ctk.CTkFrame(self)
        self.ollama_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(self.ollama_frame, text="Ollama Server URL").pack(side="left", padx=10, pady=10)
        self.ollama_entry = ctk.CTkEntry(self.ollama_frame, width=300)
        self.ollama_entry.insert(0, load_setting("ollama_url", "http://localhost:11434/v1"))
        self.ollama_entry.pack(side="right", fill="x", expand=True, padx=10, pady=10)

        self.keys_frame = ctk.CTkFrame(self); self.keys_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.keys_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.keys_frame, text="OpenAI Key").grid(row=0, column=0, padx=10, pady=5, sticky="w"); self.openai_entry = ctk.CTkEntry(self.keys_frame); self.openai_entry.grid(row=0, column=1, padx=10, sticky="ew")
        ctk.CTkLabel(self.keys_frame, text="Maritaca Key").grid(row=1, column=0, padx=10, pady=5, sticky="w"); self.maritaca_entry = ctk.CTkEntry(self.keys_frame); self.maritaca_entry.grid(row=1, column=1, padx=10, sticky="ew")
        ctk.CTkLabel(self.keys_frame, text="OpenRouter Key").grid(row=2, column=0, padx=10, pady=5, sticky="w"); self.openrouter_entry = ctk.CTkEntry(self.keys_frame); self.openrouter_entry.grid(row=2, column=1, padx=10, sticky="ew")

        # --- Controls ---
        self.save_button = ctk.CTkButton(self, text="Save Settings", command=self.save_settings); self.save_button.grid(row=5, column=0, padx=20, pady=20, sticky="e")
        self.feedback_label = ctk.CTkLabel(self, text=""); self.feedback_label.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        self.bind("<Visibility>", lambda event: self.refresh_models())
        self.provider_changed(self.provider_var.get())

    def provider_changed(self, choice):
        save_setting("active_provider", choice)
        self.feedback_label.configure(text=f"{choice} is now active.")
        is_ollama = choice == "Ollama"
        if is_ollama: self.model_entry.grid()
        else: self.model_entry.grid_remove()
        self.refresh_models()

    def model_changed(self, choice):
        if self.provider_var.get() == "Ollama":
            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, choice)
        self.save_model_setting()

    def save_model_setting(self):
        provider = self.provider_var.get().lower()
        model_to_save = self.model_entry.get() if provider == "ollama" and self.model_entry.get() else self.model_var.get()
        if "(No models" not in model_to_save and "Loading..." not in model_to_save:
            save_setting(f"{provider}_model", model_to_save)
            self.feedback_label.configure(text=f"Set {provider} model to: {model_to_save}", text_color="green")

    def save_settings(self):
        self.save_model_setting()
        save_setting("ollama_url", self.ollama_entry.get())
        for service, entry in [("OpenAI", self.openai_entry), ("Maritaca", self.maritaca_entry), ("OpenRouter", self.openrouter_entry)]:
            if entry.get(): save_api_key(service, entry.get())
        self.feedback_label.configure(text="Settings saved!", text_color="green")

    def refresh_models(self):
        self.model_menu.configure(values=["Loading..."]); self.model_var.set("Loading...")
        self.refresh_button.configure(state="disabled")

        provider_name = self.provider_var.get()
        # Read UI values in the main thread
        ollama_base_url = self.ollama_entry.get()

        coro = self._get_models_coro(provider_name, ollama_base_url)

        # Use the thread-safe queue to schedule the UI update
        run_async_task(coro, self.main_app.async_queue, self._update_models_ui)

    async def _get_models_coro(self, provider_name, ollama_base_url=None):
        provider = None
        if provider_name == "Ollama":
            provider = OllamaProvider(base_url=ollama_base_url)
        else:
            api_key = get_api_key(provider_name)
            if api_key:
                if provider_name == "OpenAI": provider = OpenAIProvider(api_key)
                elif provider_name == "Maritaca": provider = MaritacaProvider(api_key)
                elif provider_name == "OpenRouter": provider = OpenRouterProvider(api_key)
        return await provider.list_models() if provider else []

    def _update_models_ui(self, models):
        provider = self.provider_var.get().lower()
        if models:
            self.model_menu.configure(values=models)
            saved_model = load_setting(f"{provider}_model", models[0])
            self.model_var.set(saved_model if saved_model in models else models[0])
        else:
            self.model_menu.configure(values=["(List failed)"]); self.model_var.set("(List failed)")
        if provider == "ollama":
            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, load_setting(f"{provider}_model", "llama3.1"))
        self.refresh_button.configure(state="normal")

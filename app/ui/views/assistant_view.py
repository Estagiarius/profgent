import customtkinter as ctk
from app.utils.async_utils import run_async_task

class AssistantView(ctk.CTkFrame):
    def __init__(self, parent, main_app, assistant_service):
        super().__init__(parent)
        self.assistant_service = assistant_service
        self.main_app = main_app

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.chat_history = ctk.CTkTextbox(self, state="disabled", wrap="word")
        self.chat_history.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.user_input = ctk.CTkEntry(self.input_frame, placeholder_text="Pergunte qualquer coisa ao assistente...")
        self.user_input.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.user_input.bind("<Return>", lambda event: self.send_message())

        self.send_button = ctk.CTkButton(self.input_frame, text="Enviar", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        self.add_message("Sistema", "Bem-vindo! Como posso ajudar você hoje?")

    def send_message(self):
        user_text = self.user_input.get()
        if not user_text.strip(): return

        self.add_message("Você", user_text)
        self.user_input.delete(0, "end")

        self.user_input.configure(state="disabled")
        self.send_button.configure(state="disabled")
        self.add_message("Assistente", "Pensando...")

        # Use the new async utility to run the task
        coro = self.assistant_service.get_response(user_text)
        run_async_task(coro, self.main_app.async_queue, lambda result: self.main_app.after(0, self.update_ui_with_response, result))

    def update_ui_with_response(self, response):
        """Updates the chat history with the assistant's final response."""
        # Remove the "Thinking..." message
        self.chat_history.configure(state="normal")
        current_text = self.chat_history.get("1.0", "end-1c")
        lines = current_text.strip().split('\n\n')
        if lines and lines[-1].startswith("Assistente: Pensando..."):
            new_text = "\n\n".join(lines[:-1])
            self.chat_history.delete("1.0", "end")
            if new_text: self.chat_history.insert("1.0", new_text + "\n\n")

        # Add the actual response
        if response.content: self.add_message("Assistente", response.content)
        else: self.add_message("Sistema", "Uma ação foi realizada, mas nenhuma resposta verbal foi gerada.")

        self.chat_history.configure(state="disabled")
        self.user_input.configure(state="normal")
        self.send_button.configure(state="normal")

    def add_message(self, sender: str, message: str):
        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", f"{sender}: {message}\n\n")
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

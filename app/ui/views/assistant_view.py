import customtkinter as ctk
from app.services.assistant_service import AssistantService

class AssistantView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.assistant_service = AssistantService()

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Chat history text box
        self.chat_history = ctk.CTkTextbox(self, state="disabled", wrap="word")
        self.chat_history.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # User input frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.user_input = ctk.CTkEntry(self.input_frame, placeholder_text="Ask the assistant anything...")
        self.user_input.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.user_input.bind("<Return>", self.send_message_event)

        self.send_button = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        # Display initial message
        self.add_message("System", "Welcome! How can I help you today? If the assistant is not configured, please set the API key in Settings.")

    def send_message_event(self, event):
        self.send_message()

    def send_message(self):
        user_text = self.user_input.get()
        if not user_text.strip():
            return

        self.add_message("You", user_text)
        self.user_input.delete(0, "end")

        # Disable input while the assistant is thinking
        self.user_input.configure(state="disabled")
        self.send_button.configure(state="disabled")

        # Get response from the service
        # This will now handle the full agentic loop
        response = self.assistant_service.get_response(user_text)

        # The final response content will be displayed
        if response.content:
            self.add_message("Assistant", response.content)
        else:
            # Handle cases where a tool is called but no final content is returned
             self.add_message("System", "An action was performed, but no verbal response was generated.")

        # Re-enable input
        self.user_input.configure(state="normal")
        self.send_button.configure(state="normal")


    def add_message(self, sender: str, message: str):
        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", f"{sender}: {message}\n\n")
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

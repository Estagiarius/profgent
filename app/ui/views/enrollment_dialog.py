import customtkinter as ctk
from typing import List, Dict, Callable, Any

class EnrollmentDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, students: List[Dict[str, Any]], enroll_callback: Callable[[List[int]], None]):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x500")

        self.students = students
        self.enroll_callback = enroll_callback

        # Store checkboxes to retrieve values later
        # Key: student_id, Value: ctk.CTkCheckBox (or StringVar/BooleanVar linked to it)
        self.check_vars: Dict[int, ctk.BooleanVar] = {}

        self._setup_ui()
        self._populate_list()

        # Bring to front
        self.lift()
        self.focus_force()
        self.grab_set()

    def _setup_ui(self):
        # Configure grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Search Area ---
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Buscar aluno por nome...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        # Bind key release to filter in real-time
        self.search_entry.bind("<KeyRelease>", self._on_search_change)

        # --- List Area ---
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # --- Actions Area ---
        self.actions_frame = ctk.CTkFrame(self)
        self.actions_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.enroll_button = ctk.CTkButton(self.actions_frame, text="Matricular Selecionados", command=self._on_enroll)
        self.enroll_button.pack(side="right", padx=10, pady=10)

        self.cancel_button = ctk.CTkButton(self.actions_frame, text="Cancelar", command=self.destroy, fg_color="transparent", border_width=1)
        self.cancel_button.pack(side="right", padx=10, pady=10)

    def _populate_list(self, filter_text: str = ""):
        # Clear existing widgets in the scrollable frame
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        filter_text = filter_text.lower()

        # Header Row
        header_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=2)

        # We use a dummy checkbox for spacing alignment if needed, or just labels
        ctk.CTkLabel(header_frame, text="Nome", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(35, 10))
        ctk.CTkLabel(header_frame, text="Nascimento", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10)

        # Filter and display students
        row_count = 0
        for student in self.students:
            full_name = f"{student['first_name']} {student['last_name']}"

            if filter_text and filter_text not in full_name.lower():
                continue

            student_id = student['id']

            # Row Container
            row_frame = ctk.CTkFrame(self.list_frame)
            row_frame.pack(fill="x", padx=5, pady=2)

            # Checkbox variable logic
            # If we haven't seen this student before, init their var to False
            if student_id not in self.check_vars:
                self.check_vars[student_id] = ctk.BooleanVar(value=False)

            chk = ctk.CTkCheckBox(
                row_frame,
                text=full_name,
                variable=self.check_vars[student_id],
                width=20,
                height=20
            )
            chk.pack(side="left", padx=5, pady=5)

            # Birth Date Display
            birth_date_str = student.get('birth_date') or "N/A"
            # Format if it looks like YYYY-MM-DD
            if birth_date_str != "N/A" and "-" in birth_date_str:
                try:
                    # Simple split/reorder to DD/MM/YYYY for display if needed
                    parts = birth_date_str.split("-")
                    if len(parts) == 3:
                        birth_date_str = f"{parts[2]}/{parts[1]}/{parts[0]}"
                except:
                    pass

            ctk.CTkLabel(row_frame, text=birth_date_str).pack(side="right", padx=10)

            row_count += 1

        if row_count == 0:
            ctk.CTkLabel(self.list_frame, text="Nenhum aluno encontrado.").pack(pady=20)

    def _on_search_change(self, event):
        self._populate_list(self.search_entry.get())

    def _on_enroll(self):
        selected_ids = [s_id for s_id, var in self.check_vars.items() if var.get()]

        if not selected_ids:
            return # Optionally show a warning "No students selected"

        self.enroll_callback(selected_ids)
        self.destroy()

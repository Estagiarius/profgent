    def import_students(self):
        if not self.class_id:
            messagebox.showerror("Erro", "Selecione uma turma antes de importar alunos.")
            return

        filepath = filedialog.askopenfilename(
            title="Selecione um arquivo CSV de Alunos",
            filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*"))
        )
        if not filepath:
            return

        # Disable UI elements and show a temporary status message
        self.import_button.configure(state="disabled", text="Importando...")
        self.enroll_student_button.configure(state="disabled")

        # Create the coroutine for the import task
        coro = import_students_from_csv(
            filepath,
            self.class_id,
            self.main_app.data_service,
            self.main_app.assistant_service
        )

        # Run the task in the background using the standard non-blocking utility
        run_async_task(coro, self.main_app.loop, self.main_app.async_queue, self._on_import_complete)

    def _on_import_complete(self, result):
        """
        Callback function executed on the main UI thread after the import task finishes.
        """
        # Re-enable UI elements
        self.import_button.configure(state="normal", text="Importar Alunos (.csv)")
        self.enroll_student_button.configure(state="normal")

        # The result can be either the expected tuple or an exception
        if isinstance(result, Exception):
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro fatal durante a importação:\n\n{result}")
            return

        # Unpack the result and show the final message
        success_count, errors = result
        self.populate_student_list()

        if errors:
            error_message = f"{success_count} alunos importados com sucesso, mas ocorreram os seguintes erros:\n\n" + "\n".join(errors)
            messagebox.showwarning("Importação com Erros", error_message)
        else:
            messagebox.showinfo("Sucesso", f"{success_count} alunos importados com sucesso!")

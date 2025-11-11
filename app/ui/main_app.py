import asyncio
import customtkinter as ctk
from queue import Queue, Empty
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.assistant_view import AssistantView
from app.ui.views.settings_view import SettingsView
from app.ui.views.management_view import ManagementView
from app.ui.views.class_selection_view import ClassSelectionView
from app.ui.views.class_detail_view import ClassDetailView

from app.services.data_service import DataService
from app.services.assistant_service import AssistantService

class MainApp(ctk.CTk):
    def __init__(self, data_service: DataService, assistant_service: AssistantService):
        super().__init__()

        self.data_service = data_service
        self.assistant_service = assistant_service

        self.title("Gestão Acadêmica")
        self.geometry("1100x800")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.loop = asyncio.get_event_loop()

        self.async_queue = Queue()
        self._process_queue()

        self.update_asyncio()

        # Set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(8, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="Navegação",
                                                  font=ctk.CTkFont(size=20, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Add navigation buttons
        self.dashboard_button = ctk.CTkButton(self.navigation_frame, text="Dashboard", command=lambda: self.show_view("dashboard"))
        self.dashboard_button.grid(row=1, column=0, padx=20, pady=10)

        self.management_button = ctk.CTkButton(self.navigation_frame, text="Gestão de Dados", command=lambda: self.show_view("management"))
        self.management_button.grid(row=2, column=0, padx=20, pady=10)

        self.class_selection_button = ctk.CTkButton(self.navigation_frame, text="Minhas Turmas", command=lambda: self.show_view("class_selection"))
        self.class_selection_button.grid(row=3, column=0, padx=20, pady=10)

        self.assistant_button = ctk.CTkButton(self.navigation_frame, text="Assistente IA", command=lambda: self.show_view("assistant"))
        self.assistant_button.grid(row=4, column=0, padx=20, pady=10)

        self.settings_button = ctk.CTkButton(self.navigation_frame, text="Configurações", command=lambda: self.show_view("settings"))
        self.settings_button.grid(row=7, column=0, padx=20, pady=10)


        # Create main content frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Create views and store them in a dictionary
        self.views = {
            "dashboard": DashboardView(self.main_frame),
            "management": ManagementView(self.main_frame),
            "class_selection": ClassSelectionView(self.main_frame, self),
            "class_detail": ClassDetailView(self.main_frame, self),
            "assistant": AssistantView(self.main_frame, self, assistant_service=self.assistant_service),
            "settings": SettingsView(self.main_frame, self)
        }

        # Show the dashboard view by default
        self.show_view("dashboard")

    def _process_queue(self):
        try:
            # Get a task from the queue without blocking
            callable, args = self.async_queue.get_nowait()
            callable(*args)
        except Empty:
            pass  # Do nothing if the queue is empty
        finally:
            # Schedule the next check
            self.after(100, self._process_queue)

    def show_view(self, view_name, **kwargs):
        # Hide all views
        for view in self.views.values():
            view.grid_forget()

        # Show the requested view
        selected_view = self.views[view_name]
        selected_view.grid(row=0, column=0, sticky="nsew")

        # Trigger the 'on_show' event if the view has one
        if hasattr(selected_view, 'on_show'):
            selected_view.on_show(**kwargs)

    def update_asyncio(self):
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()
        self._poll_id = self.after(1, self.update_asyncio)

    def on_closing(self):
        # 1. Stop the asyncio polling loop from rescheduling itself
        if hasattr(self, '_poll_id'):
            self.after_cancel(self._poll_id)

        # 2. Create and schedule the final cleanup task
        async def cleanup():
            # Close the assistant service if it was initialized
            if self.assistant_service and self.assistant_service.provider:
                await self.assistant_service.close()

            # Cancel any other pending asyncio tasks
            tasks = [t for t in asyncio.all_tasks(loop=self.loop) if t is not asyncio.current_task()]
            for task in tasks:
                task.cancel()

            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

        # Start the cleanup in the asyncio event loop
        cleanup_task = self.loop.create_task(cleanup())

        # 3. Start a non-blocking poll to check for cleanup completion
        self._check_cleanup_done(cleanup_task)

    def _check_cleanup_done(self, task):
        # 4. If the cleanup task is done, it's safe to destroy the window.
        #    Otherwise, schedule another check. This cooperative polling
        #    prevents blocking the Tkinter mainloop.
        if task.done():
            self.loop.close()
            self.destroy()
        else:
            self.after(50, self._check_cleanup_done, task)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()

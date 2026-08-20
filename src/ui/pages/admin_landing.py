from src.ui.pages.base_pages import SubPage
from nicegui import ui



class AdminLanding(SubPage):
    pageName = "admin_landing"

    def build_content(self) -> None:
        
        with ui.card().classes("w-full h-[85vh] items-center relative flex flex-col p-0"):
            
            ui.label(f"Welcome to the Admin Page {self.controller.load_user()}!").classes("w-full text-center text-2xl font-bold")
            
            ui.separator().classes("my-4")
            
            ui.label("Choose your action:").classes("text-lg")
            
            ui.separator().classes("my-4")
            
            with ui.column().classes("w-full gap-4 items-center"):
                ui.button(
                    "Delete Measurements",
                    icon="delete",
                    on_click=lambda: self.controller.handle_navigation_request("plot-select", mode="admin"),
                ).classes("w-72")
                
                ui.button(
                    "Manage VVTs",
                    icon="table_chart",
                    on_click=lambda: self.controller.handle_navigation_request("admin_vvt"),
                ).classes("w-72")
                
                
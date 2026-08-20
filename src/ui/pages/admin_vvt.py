from nicegui import ui

from src.ui.pages.base_pages import SubPage

class AdminVVT(SubPage):
    
    pageName = "admin_vvt"

    def build_content(self) -> None:
        
        with ui.card().classes("w-full flex-1 min-h-0 overflow-auto items-center relative flex flex-col p-0"):
            
            with ui.row().classes("w-full p-4 items-center gap-4 bg-gray-50 shrink-0"):
                
                ui.label(f"Welcome to the Admin VVT Page {self.controller.load_user()}!").classes("w-full text-center text-2xl font-bold")
                
                ui.separator().classes("my-4")
                
                self.tableContainer = ui.row().classes("w-full h-[70vh] overflow-auto p-4")
                self.controller.handle_admin_vvt_table(self.tableContainer)
                
                ui.separator().classes("my-4")
                
                ui.button(
                    "Rewrite VVTs",
                    icon="save",
                    on_click=lambda: self.controller.handle_admin_rewrite_vvts(),
                )
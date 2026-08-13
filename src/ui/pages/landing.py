from nicegui import ui
from src.ui.pages.base_pages import BasePage


class LandingPage(BasePage):
    pageName = "landing"
    dbType: str = "CSV"

    def render(self, parent: ui.column) -> None:
        with parent:
            
            ui.label("Welcome to the Temp-Profiler!").classes("w-full text-center text-2xl font-bold")
            
            with ui.column().classes("items-center gap-4 mx-auto my-8"):
                ui.label("Choose your action:").classes("text-lg")
                
                with ui.card():
                    ui.button(
                        "Import measurement-data",
                        icon="upload",
                        on_click=lambda: start_analyzing("import-get"),
                    ).classes("w-72")
                    
                    ui.button(
                        "Show measurements from database",
                        icon="show_chart",
                        on_click=lambda: start_analyzing("plot-select"),
                    ).classes("w-72")
                    
                    ui.label("choose the database type").classes("text-sm text-gray-500")
                
                    ui.radio(
                        ["Auto", "CSV", "Databricks"]
                    ).props("inline").bind_value(self, "dbType")
                    
                    
        def start_analyzing(pageName: str):
            self.controller.init_database(self.dbType)
            self.controller.handle_navigation_request(pageName)
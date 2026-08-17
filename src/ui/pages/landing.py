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
                        on_click=lambda: start_analyzing("plot-select", mode="user"),
                    ).classes("w-72")
                    
                    ui.label("choose the database type:").classes("text-sm text-gray-500")
                
                    self.options = ["Auto", "CSV", "Databricks"]
                    self.dbType = self.options[0]  # defaults to auto
                
                    ui.radio(
                        self.options
                    ).props("inline").bind_value(self, "dbType")
                    
                    ui.separator().classes("my-4")
                    
                    ui.button(
                        "ADMIN",
                        icon="admin_panel_settings",
                        on_click= self.handle_admin_check,
                    ).classes("w-72")
                    
                    
        def start_analyzing(pageName: str, mode: str = "user"):
            self.controller.init_database(self.dbType)
            self.controller.handle_navigation_request(pageName, mode=mode)
            
    async def handle_admin_check(self):
        # create db
        self.controller.init_database(self.dbType)
        
        # call callback in controller for admin check
        await self.controller.handle_admin_check()
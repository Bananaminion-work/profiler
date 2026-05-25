from nicegui import ui
from src.ui.pages.base_pages import BasePage


class LandingPage(BasePage):
    pageName = "landing"

    def render(self, parent: ui.column) -> None:
        with parent:
            with ui.column().classes("items-center gap-4 mx-auto my-8"):
                ui.label("Choose your action:")
                ui.button(
                    "Create measurement-data",
                    icon="upload",
                    on_click=lambda: self.controller.handle_navigation_request("import-get"),
                ).classes("w-72")
                ui.button(
                    "Show measurements from database",
                    icon="show_chart",
                    on_click=lambda: self.controller.handle_navigation_request("plot-select"),
                ).classes("w-72")
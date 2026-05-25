from src.ui.pages.base_pages import SubPage, BasePage
from nicegui import ui

class PlotPage_showData(SubPage):
    pageName = "plot-show"

    def build_content(self) -> None:
        with ui.column().classes("w-full gap-4"):
            with ui.card().classes("w-full min-h-[500px]"):
                ui.label("Plot area")
            with ui.row().classes("items-center"):
                ui.label("Choose zeropoint:")
                ui.select(
                    ["bulkhead", "ventilate 2", "first injection", "above 235C"],
                    value="bulkhead",
                ).classes("w-80")


class Popup_confirm(BasePage):

    def render(self, parent: ui.column) -> None:
        with parent:
            with ui.card().classes("mx-auto my-16 w-[640px] items-center"):
                ui.label(self.message or "Are you sure?")
                with ui.row().classes("justify-center w-full"):
                    ui.button("YES", on_click=lambda: self.controller.handle_navigation_request("landing"))
                    ui.button(
                        "NO",
                        color="negative",
                        on_click=lambda: self.controller.handle_navigation_request(self.returnPage),
                    )

    def set_message(self, message: str) -> None:
        self.message = message

    def set_returnPage(self, pageName: str) -> None:
        self.returnPage = pageName


class Popup_warning(BasePage):

    def render(self, parent: ui.column) -> None:
        with parent:
            with ui.card().classes("mx-auto my-16 w-[640px] items-center"):
                ui.label(self.message or "Warning")
                ui.button("OK", on_click=lambda: self.controller.handle_navigation_request(self.returnPage))

    def set_message(self, message: str) -> None:
        self.message = message

    def set_returnPage(self, pageName: str) -> None:
        self.returnPage = pageName
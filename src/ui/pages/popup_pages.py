from src.ui.pages.base_pages import SubPage, BasePage
from nicegui import ui


class Popup_confirm(BasePage):
    
    pageName = "Popup_confirm"

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
    
    pageName = "Popup_warning"

    def render(self, parent: ui.column) -> None:
        with parent:
            with ui.card().classes("mx-auto my-16 w-[640px] items-center"):
                ui.label(self.message or "Warning")
                ui.button("OK", on_click=lambda: self.controller.handle_navigation_request(self.returnPage))

    def set_message(self, message: str) -> None:
        self.message = message

    def set_returnPage(self, pageName: str) -> None:
        self.returnPage = pageName
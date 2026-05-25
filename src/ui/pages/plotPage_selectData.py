from nicegui import ui
from src.ui.pages.base_pages import SubPage


class PlotPage_selectData(SubPage):
    pageName = "plot-select"
    date: str = ""
    oven_nr: str = "1234"
    product: str = ""
    nozzlefield: str = ""
    profile_name: str = ""

    def build_content(self) -> None:
        with ui.column().classes("w-full gap-4"):
            with ui.card().classes("w-full"):
                with ui.grid(columns=3).classes("w-full gap-3"):
                    ui.input("Pick the date").props("type=date").bind_value(self, "date")
                    ui.select(["1234", "2345", "3456", "4567"], value="1234", label="Select the oven-number").bind_value(self, "oven_nr")
                    ui.input("Enter the product name", placeholder="Product name").bind_value(self, "product")
                    ui.input("Nozzlefield", placeholder="Nozzlefield").bind_value(self, "nozzlefield")
                    ui.input("Profilename", placeholder="Profilename").bind_value(self, "profile_name")

            with ui.card().classes("w-full min-h-96"):
                ui.label("Table placeholder")

            with ui.row().classes("justify-end w-full"):
                ui.button("Show selected", on_click=lambda: self.controller.handle_navigation_request("plot-show"))
                ui.button(
                    "Discard",
                    color="negative",
                    on_click=lambda: self.controller.handle_popup(
                        "confirm",
                        "Are you sure to discard and return to home?",
                        self.pageName,
                    ),
                )

    def reset(self) -> None:
        self.date = ""
        self.oven_nr = "1234"
        self.product = ""
        self.nozzlefield = ""
        self.profile_name = ""
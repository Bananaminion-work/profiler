from __future__ import annotations

from abc import ABC, abstractmethod
import time
from typing import TYPE_CHECKING

from nicegui import ui

if TYPE_CHECKING:
    from src.ui.appcontroller import AppController


class BasePage(ABC):
    controller: AppController

    def __init__(self, controller: AppController):
        self.controller = controller

    @abstractmethod
    def render(self, parent: ui.column) -> None:
        pass

    def reset(self) -> None:
        pass


class SubPage(BasePage):
    @abstractmethod
    def build_content(self) -> None:
        pass

    def render(self, parent: ui.column) -> None:
        with parent:
            ui.button(
                "Home",
                icon="home",
                on_click=lambda: self.controller.handle_navigation_request("landing"),
            ).props("outline")
            ui.separator()
            self.build_content()


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


class ImportPage_getData(SubPage):
    pageName = "import-get"

    def __init__(self, controller: AppController):
        super().__init__(controller)
        self.input_path = None
        self.radio_source = None
        self.uploaded_file_name = ""

    def build_content(self) -> None:
        with ui.column().classes("gap-4"):
            ui.label("Please enter the path of the ZIP-file:")
            with ui.row().classes("items-center gap-2"):
                self.input_path = ui.input(placeholder="dbms\\ path\\ to\\ file...").classes("w-96")
                ui.button("Submit", icon="check", on_click=self.on_submit_click)

            ui.label("Please select your source of Data:")
            self.radio_source = ui.radio(
                ["Solderstar", "Rehm-recorder", "Datapaq"],
                value="Solderstar",
            )

            ui.label("Enter file instead of path:")

            def on_upload(e) -> None:
                self.uploaded_file_name = e.name
                self.controller.log(f"uploaded file: {e.name}")

            ui.upload(on_upload=on_upload, multiple=False).props("accept=.zip")

    def on_submit_click(self) -> None:
        chosen_source = self.radio_source.value if self.radio_source else ""
        self.controller.log("send path..")
        self.controller.log(f"chosen source is {chosen_source}")
        self.controller.log("calls handle_data_import_request")
        self.controller.handle_data_import_request()
        time.sleep(2)
        self.controller.handle_navigation_request("import-show")
        if self.input_path:
            self.input_path.value = ""

    def reset(self) -> None:
        if self.input_path:
            self.input_path.value = ""
        self.uploaded_file_name = ""


class ImportPage_showData(SubPage):
    pageName = "import-show"

    def __init__(self, controller: AppController):
        super().__init__(controller)
        self.accordionNames: list[ui.input] = []
        self.input_nozzlefield = None
        self.input_profileName = None
        self.input_comment = None

    def _create_accordion(self) -> None:
        self.accordionNames = []

        def add_fields(prefix: str) -> None:
            for i in range(1, 5):
                field = ui.input(f"{prefix} {i}:", placeholder="enter value...").classes("w-80")
                self.accordionNames.append(field)

        with ui.expansion("Injections", icon="expand_more"):
            add_fields("Injection")
        with ui.expansion("Waiting-time", icon="expand_more"):
            add_fields("Waiting-time")
        with ui.expansion("Cooling-frequency", icon="expand_more"):
            add_fields("Cooling-frequency")
        with ui.expansion("Cooling-time", icon="expand_more"):
            add_fields("Cooling-time")

    def build_content(self) -> None:
        with ui.column().classes("w-full gap-4"):
            with ui.row().classes("w-full gap-6 items-start"):
                with ui.card().classes("w-2/5 min-h-72"):
                    ui.label("Plot preview")

                with ui.card().classes("w-3/5"):
                    with ui.grid(columns=2).classes("w-full gap-3"):
                        drd_ovenNr = ui.select(["1234", "2345", "3456", "4567"], value="1234", label="Select the oven-number")
                        drd_product = ui.select(["VW-ECO", "VOLVO-ERAD", "BASE", "PM6"], value="PM6", label="Select the product")
                        drd_load = ui.select(["1", "2", "3", "4", "5", "6", "7", "8"], value="8", label="Load of the profile type")
                        drd_pos = ui.select(["1", "2", "3", "4", "5", "6", "7", "8"], value="8", label="Position of measurement cooler")
                        drd_count = ui.select(["1", "2", "3", "4", "5", "6", "7", "8"], value="8", label="Amount of coolers")
                        radio_prod_test = ui.radio(["Serialproduction", "Test"], value="Test").props("inline")

                    ui.separator()
                    self.input_nozzlefield = ui.input("Nozzlefield", placeholder="Dreifachdüsenfeld")
                    self.input_profileName = ui.input("Profilename", placeholder="used profilename")
                    self._create_accordion()
                    self.input_comment = ui.textarea("Comment", placeholder="enter your comment..")

                    with ui.row().classes("justify-end w-full"):
                        ui.button("Save", on_click=self.on_save_click)
                        ui.button("Discard", color="negative", on_click=self.on_discard_click)

            with ui.card().classes("w-full"):
                ui.label("Choose zeropoints")
                with ui.grid(columns=5).classes("w-full gap-3"):
                    ui.select(
                        ["muss uebergeben werden", "2", "3", "4", "5", "6", "7", "8"],
                        value="muss uebergeben werden",
                        label="Plot",
                    )
                    ui.select(
                        ["muss uebergeben werden", "2", "3", "4", "5", "6", "7", "8"],
                        value="muss uebergeben werden",
                        label="Bulkhead",
                    )
                    ui.select(
                        ["muss uebergeben werden", "2", "3", "4", "5", "6", "7", "8"],
                        value="muss uebergeben werden",
                        label="First injection",
                    )
                    ui.select(
                        ["muss uebergeben werden", "2", "3", "4", "5", "6", "7", "8"],
                        value="muss uebergeben werden",
                        label="Above 235",
                    )
                    ui.select(
                        ["muss uebergeben werden", "2", "3", "4", "5", "6", "7", "8"],
                        value="muss uebergeben werden",
                        label="Ventilate 2",
                    )

            _ = drd_ovenNr, drd_product, drd_load, drd_pos, drd_count, radio_prod_test

    def on_save_click(self) -> None:
        self.controller.log("Data gets written to the database...")
        self.controller.log("this is to be implemented soon...")
        self.controller.handle_popup("warning", "Data has been saved to the database", "landing")

    def on_discard_click(self) -> None:
        self.controller.handle_popup("confirm", "Are you sure to discard and return to home?", self.pageName)

    def reset(self) -> None:
        if self.input_nozzlefield:
            self.input_nozzlefield.value = ""
        if self.input_profileName:
            self.input_profileName.value = ""
        if self.input_comment:
            self.input_comment.value = ""
        for text_field in self.accordionNames:
            text_field.value = ""


class PlotPage_selectData(SubPage):
    pageName = "plot-select"

    def __init__(self, controller: AppController):
        super().__init__(controller)
        self.datePicker = None
        self.input_nozzlefield = None
        self.input_product = None
        self.input_profileName = None

    def build_content(self) -> None:
        with ui.column().classes("w-full gap-4"):
            with ui.card().classes("w-full"):
                with ui.grid(columns=3).classes("w-full gap-3"):
                    self.datePicker = ui.input("Pick the date").props("type=date")
                    ui.select(["1234", "2345", "3456", "4567"], value="1234", label="Select the oven-number")
                    self.input_product = ui.input("Enter the product name", placeholder="Product name")
                    self.input_nozzlefield = ui.input("Nozzlefield", placeholder="Nozzlefield")
                    self.input_profileName = ui.input("Profilename", placeholder="Profilename")

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
        if self.input_nozzlefield:
            self.input_nozzlefield.value = ""
        if self.input_product:
            self.input_product.value = ""
        if self.input_profileName:
            self.input_profileName.value = ""
        if self.datePicker:
            self.datePicker.value = ""


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
    def __init__(self, controller: AppController):
        super().__init__(controller)
        self.message = ""
        self.returnPage = "landing"

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
    def __init__(self, controller: AppController):
        super().__init__(controller)
        self.message = ""
        self.returnPage = "landing"

    def render(self, parent: ui.column) -> None:
        with parent:
            with ui.card().classes("mx-auto my-16 w-[640px] items-center"):
                ui.label(self.message or "Warning")
                ui.button("OK", on_click=lambda: self.controller.handle_navigation_request(self.returnPage))

    def set_message(self, message: str) -> None:
        self.message = message

    def set_returnPage(self, pageName: str) -> None:
        self.returnPage = pageName
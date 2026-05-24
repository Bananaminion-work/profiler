from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from nicegui import ui
from nicegui.events import UploadEventArguments

from src.shared.upload_container import UploadContainer

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
    path: str = ""
    source: str = "Solderstar"
    uploadWidget: ui.upload
    uploaded_file_name: str = ""
    uploaded_content: bytes | None = None

    def build_content(self) -> None:
          
        with ui.column().classes("gap-4 w-96 mx-auto my-8 items-center"):
                ui.label("Please use the upload-button to upload the zip-file of your measurement:").classes("text-lg")
                ui.separator()
                ui.label("Please select your source of Data:")
                ui.radio(
                    ["Solderstar", "Rehm-recorder", "Datapaq"],
                ).bind_value(self, "source")

                self.uploadWidget = ui.upload(
                    on_upload=self.on_upload, 
                    multiple=False,
                    auto_upload=True
                ).props("accept=.zip").classes("w-full")

                ui.separator()

                ui.button(
                    "Submit",
                    icon="check",
                    on_click=self.on_submit_click
                    ).classes("w-full")
        
    async def on_upload(self, e: UploadEventArguments) -> None:
        """handles the upload-event of the upload-widget, 
        saves the file name and content in the page-attributes.
        needs to be async because of the await for reading the file content"""
        self.uploaded_file_name = e.file.name
        self.uploaded_content = await e.file.read()
    
    def on_submit_click(self) -> None:
        
        if self.uploaded_content is None:
            ui.notify("Please upload a file before submitting.", color="negative")
            return
        
        
        uploadContainer = UploadContainer(self.uploaded_file_name, self.uploaded_content)
        
        # check if file was uploaded
        if isinstance(uploadContainer.content, bytes):
            self.controller.log(f"Submit clicked with uploaded file name: {self.uploaded_file_name}")
            self.controller.log(f"chosen source is {self.source}")
            self.controller.log("strating calculation of Data-Objects...")
            
            self.controller.handle_data_import_request(uploadContainer, self.source)
            
            self.controller.handle_navigation_request("import-show")


    def reset(self) -> None:
        self.source = "Solderstar"
        self.uploaded_file_name = ""
        self.uploaded_content = b""


class ImportPage_showData(SubPage):
    pageName = "import-show"
    oven_nr: str = "1234"
    product: str = "PM6"
    load: str = "8"
    pos: str = "8"
    count: str = "8"
    prod_test: str = "Test"
    nozzlefield: str = ""
    profile_name: str = ""
    comment: str = ""
    injection_1: str = ""
    injection_2: str = ""
    injection_3: str = ""
    injection_4: str = ""
    waiting_1: str = ""
    waiting_2: str = ""
    waiting_3: str = ""
    waiting_4: str = ""
    cooling_freq_1: str = ""
    cooling_freq_2: str = ""
    cooling_freq_3: str = ""
    cooling_freq_4: str = ""
    cooling_time_1: str = ""
    cooling_time_2: str = ""
    cooling_time_3: str = ""
    cooling_time_4: str = ""
    config: str = ""
    date: str= ""
    startTime: str= ""
    bulkheadZeropoint: str = ""
    firstInjectionZeropoint: str = ""
    above235Zeropoint: str = ""
    ventilate2Zeropoint: str = ""
    chosenZeropoint_show: str = ""

    def _create_accordion(self) -> None:
        groups = [
            ("Injections",        "Injection",         ["injection_1",    "injection_2",    "injection_3",    "injection_4"]),
            ("Waiting-time",      "Waiting-time",      ["waiting_1",      "waiting_2",      "waiting_3",      "waiting_4"]),
            ("Cooling-frequency", "Cooling-frequency", ["cooling_freq_1", "cooling_freq_2", "cooling_freq_3", "cooling_freq_4"]),
            ("Cooling-time",      "Cooling-time",      ["cooling_time_1", "cooling_time_2", "cooling_time_3", "cooling_time_4"]),
        ]
        for title, prefix, attrs in groups:
            with ui.expansion(title, icon="expand_more"):
                for i, attr in enumerate(attrs, 1):
                    ui.input(f"{prefix} {i}:", placeholder="enter value...").classes("w-full").bind_value(self, attr)

    def build_content(self) -> None:
        
        
        with ui.column().classes("w-full gap-4"):
            
            # section 1: Plot
            with ui.card().classes("w-full h-[65vh]") as plotCard:
                self.plotContainer = ui.column().classes("w-full h-full")
                self.update_plot_preview()

            # section 2: Config
            with ui.card().classes("w-full"):
                ui.label("Choose config and zeropoint").classes('text-lg')
                with ui.row().classes("w-full"):
                    ui.select(
                        ["standard", "standard2", "3", "4", "5", "6", "7", "8"],
                        value="standard",
                        label="choose config for plot",
                        on_change=self.update_plot_preview
                    ).bind_value(self,"config").classes("w-100")
                    
                    ui.select(
                        options=["muss uebergeben werden", "2", "3", "4", "5", "6", "7", "8"],
                        value="muss uebergeben werden",
                        label="choose zeropoint for plot"
                    ).bind_value(self,"chosenZeropoint_show").classes("w-100")
                    
                    ui.button(
                                icon='fullscreen',
                                on_click=lambda: ui.run_javascript(f'getElement({plotCard.id}).$el.requestFullscreen()')
                            ).props('flat round')
            
            # section 3: Metadata and details
            with ui.card().classes("w-full"):
                ui.label("input Metadata to be saved to database").classes('text-lg')
            
                with ui.grid(columns=2).classes("w-full gap-3"):
                    ui.date().bind_value(self, "date")
                    ui.time().bind_value(self, "startTime")
                    ui.select(["1234", "2345", "3456", "4567"], value="1234", label="Select the oven-number").bind_value(self, "oven_nr")
                    ui.select(["VW-ECO", "VOLVO-ERAD", "BASE", "PM6"], value="PM6", label="Select the product").bind_value(self, "product")
                    ui.select(["1", "2", "3", "4", "5", "6", "7", "8"], value="8", label="Load of the profile type").bind_value(self, "load")
                    ui.select(["1", "2", "3", "4", "5", "6", "7", "8"], value="8", label="Position of measurement cooler").bind_value(self, "pos")
                    ui.select(["1", "2", "3", "4", "5", "6", "7", "8"], value="8", label="Amount of coolers").bind_value(self, "count")
                    ui.radio(["Production", "Test"], value="Test").props("inline").bind_value(self, "prod_test")

                ui.separator()
                with ui.row().classes("w-full"):
                    ui.input("Nozzlefield", placeholder="Dreifachdüsenfeld").bind_value(self, "nozzlefield").classes("w-200")
                    ui.input("Profilename", placeholder="used profilename").bind_value(self, "profile_name").classes("w-200")
                self._create_accordion()
                ui.textarea("Comment", placeholder="enter your comment..").bind_value(self, "comment").classes("w-full")

                ui.label("Choose ONLY ONE zeropoint per type to be saved in the database")
                
                ui.select(
                    ["muss uebergeben werden", "2", "3", "4", "5", "6", "7", "8"],
                    value="muss uebergeben werden",
                    label="bulkhead",
                ).classes("w-full").bind_value(self,"bulkheadZeropoint")
                
                ui.select(
                    ["muss uebergeben werden", "2", "3", "4", "5", "6", "7", "8"],
                    value="muss uebergeben werden",
                    label="First injection",
                ).classes("w-full").bind_value(self,"firstInjectionZeropoint")
                ui.select(
                    ["muss uebergeben werden", "2", "3", "4", "5", "6", "7", "8"],
                    value="muss uebergeben werden",
                    label="Above 235",
                ).classes("w-full").bind_value(self,"above235Zeropoint")
                ui.select(
                    ["muss uebergeben werden", "2", "3", "4", "5", "6", "7", "8"],
                    value="muss uebergeben werden",
                    label="Ventilate 2",
                ).classes("w-full").bind_value(self,"ventilate2Zeropoint")
                    
                    
                # separator and buttons
                ui.separator().classes("my-4")
                
                with ui.row().classes("justify-end w-full"):
                    ui.button("Save", on_click=self.on_save_click)
                    ui.button("Discard", color="negative", on_click=self.on_discard_click)
                    
        self.update_plot_preview
        
    def update_plot_preview(self):
        """clears plot container and redraws with fresh plot"""
        self.plotContainer.clear()
        # with function enables the call of handle-method on the container object
        with self.plotContainer:
            self.controller.handle_import_preview(self.config)

    def on_save_click(self) -> None:
        # fields that must have a value
        requiredFields = [
            "oven_nr",
            "product",
            "load",
            "pos",
            "count",
            "prod_test",
            "nozzlefield",
            "profile_name",
            "injection_1",
            "injection_2",
            "injection_3",
            "injection_4",
            "waiting_1",
            "waiting_2",
            "waiting_3",
            "waiting_4",
            "cooling_freq_1",
            "cooling_freq_2",
            "cooling_freq_3",
            "cooling_freq_4",
            "cooling_time_1",
            "cooling_time_2",
            "cooling_time_3",
            "cooling_time_4",
            "date",
            "startTime"
        ]
        
        for field in requiredFields:
            value = getattr(self, field)
            
            # cancel if field value is missing
            if not value:
                ui.notify(f"Please fill in the required field: {field}", color="negative")
                return
        
        metadata = {
            "ovenNr": self.oven_nr,
            "product": self.product,
            "loadProfile": self.load,
            "positionMeasurementCooler": self.pos,
            "coolerCountOnTray": self.count,
            "testCooler_flag": self.prod_test,
            "nozzlefield": self.nozzlefield,
            "profileName": self.profile_name,
            "comment": self.comment,
            "injection_1": self.injection_1,
            "injection_2": self.injection_2,
            "injection_3": self.injection_3,
            "injection_4": self.injection_4,
            "waiting_1": self.waiting_1,
            "waiting_2": self.waiting_2,
            "waiting_3": self.waiting_3,
            "waiting_4": self.waiting_4,
            "cooling_freq_1": self.cooling_freq_1,
            "cooling_freq_2": self.cooling_freq_2,
            "cooling_freq_3": self.cooling_freq_3,
            "cooling_freq_4": self.cooling_freq_4,
            "cooling_time_1": self.cooling_time_1,
            "cooling_time_2": self.cooling_time_2,
            "cooling_time_3": self.cooling_time_3,
            "cooling_time_4": self.cooling_time_4,
            "date": self.date,
            "startTime": self.startTime,
            "prod_test": self.prod_test
        }
        
        chosenZeropoints={
            "bulkhead": self.bulkheadZeropoint,
            "first injection": self.firstInjectionZeropoint,
            "above 235": self.above235Zeropoint,
            "ventilate 2": self.ventilate2Zeropoint
        }
        
        try:
            self.controller.handle_save_request(metadata, chosenZeropoints)
        
        except:
            raise Exception("The function to handle the save request did not get called successfully.")
            

    def on_discard_click(self) -> None:
        self.controller.handle_popup("confirm", "Are you sure to discard and return to home?", self.pageName)

    def reset(self) -> None:
        self.oven_nr = "1234"
        self.product = "PM6"
        self.load = "8"
        self.pos = "8"
        self.count = "8"
        self.prod_test = "Test"
        self.nozzlefield = ""
        self.profile_name = ""
        self.comment = ""
        self.injection_1 = ""
        self.injection_2 = ""
        self.injection_3 = ""
        self.injection_4 = ""
        self.waiting_1 = ""
        self.waiting_2 = ""
        self.waiting_3 = ""
        self.waiting_4 = ""
        self.cooling_freq_1 = ""
        self.cooling_freq_2 = ""
        self.cooling_freq_3 = ""
        self.cooling_freq_4 = ""
        self.cooling_time_1 = ""
        self.cooling_time_2 = ""
        self.cooling_time_3 = ""
        self.cooling_time_4 = ""
        self.config = "standard"


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
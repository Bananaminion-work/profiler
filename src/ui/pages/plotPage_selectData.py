from typing import Callable, Optional

from nicegui import ui
from src.shared.filter_composition import FilterComposition
from src.ui.pages.base_pages import SubPage
from src.shared.meta_names import MetaNames
from datetime import datetime


class PlotPage_selectData(SubPage):
    pageName = "plot-select"
    date: Optional[dict] = None
    time: Optional[datetime] = None
    oven_nr: str = ""
    oven_Recipe: str = ""
    product: str = ""
    load_profile: str = ""
    comment: str = ""
    description: str = ""
    file_name: str = ""
    
    confirmationLabel = "Save"
    configured_callback: Callable
    
    def configure(self, mode: str = "user"):
        """configures the page for the given mode, either "user" or "admin" """
        
        if mode == "admin":
            self.confirmationLabel = "Delete selected measurements"
            self.configured_callback = self.controller.handle_delete_measurements
            
        elif mode == "user":
            self.confirmationLabel = "Show selected measurements"
            self.configured_callback = self.controller.handle_show_selected_request
    

    def build_content(self) -> None:
        
        with ui.column().classes("w-full gap-4"):
            
            # section 1 - filters
            with ui.card().classes("w-full"):
                ui.label("Select the filters for the measurement table").classes("text-lg col-span-3")
                
                with ui.grid(columns=2).classes("w-full gap-4 p-4"):
                        
                    with ui.column().classes("w-full gap-4 centering"):
                        # load options for autocomplete
                        ovenOptions = self.controller.load_oven_options()
                        # ovennr
                        ui.input("Enter the oven number", placeholder="Oven number", on_change=self.update_table, autocomplete=ovenOptions).props("debounce=150").bind_value(self, "oven_nr").classes("w-full")
                        # ovenRecipe
                        ui.input("Enter the oven recipe", placeholder="Oven recipe", on_change=self.update_table).props("debounce=150").bind_value(self, "oven_Recipe").classes("w-full")
                        # product
                        ui.input("Enter the product name", placeholder="Product name", on_change=self.update_table).props("debounce=150").bind_value(self, "product").classes("w-full")
                        # load profile
                        ui.input("Enter the load profile", placeholder="Load profile", on_change=self.update_table).props("debounce=150").bind_value(self, "load_profile").classes("w-full")
                        # comment
                        ui.input("Enter the comment", placeholder="Comment", on_change=self.update_table).props("debounce=150").bind_value(self, "comment").classes("w-full")
                        # description
                        ui.input("Enter the description", placeholder="Description", on_change=self.update_table).props("debounce=150").bind_value(self, "description").classes("w-full")
                        # file name
                        ui.input("Enter the file name", placeholder="File name", on_change=self.update_table).props("debounce=150").bind_value(self, "file_name").classes("w-full")
                        
                    with ui.grid(columns=2).classes("w-full gap-4"):
                        with ui.row().classes("w-full gap-4 items-center justify-center"):
                            # date
                            ui.date("Pick the date or range", on_change=self.update_table).props("range").bind_value(self, "date")
                            # reset
                            ui.button("Reset Date", on_click=self.reset_date).classes("w-full")
                        with ui.row().classes("w-full gap-4 items-center justify-center"):
                            # time
                            ui.time("Enter the time", on_change=self.update_table).props("format24h").bind_value(self, "time")
                            # reset
                            ui.button("Reset Time", on_click=self.reset_time).classes("w-full")

            # section 2 - table
            with ui.card().classes("w-full min-h-96"):
                self.tableContainer = ui.column().classes("w-full h-full")
                self.update_table()

            # section 3 - buttons
            with ui.row().classes("justify-end w-full"):
                ui.button(
                    self.confirmationLabel,
                    on_click=lambda: self.configured_callback()
                    )
                
                ui.button(
                    "Return to Home",
                    color="negative",
                    on_click=lambda: self.controller.handle_popup(
                        "confirm",
                        "Are you sure to discard and return to home?",
                        self.pageName,
                    )
                )

        # init the table
        self.update_table()
    
    def update_table(self):
        """clears plot container and redraws with fresh plot"""
        
        #check whether the container already exists
        if not hasattr(self, "tableContainer") or self.tableContainer is None:
            return
        
        self.tableContainer.clear()
        
        # create filter composition object with the current filter values
        filter_data = {
            str(MetaNames.DATE): self.date,
            str(MetaNames.START_TIME): self.time,
            str(MetaNames.OVEN_NR): self.oven_nr,
            str(MetaNames.OVEN_RECIPE): self.oven_Recipe,
            str(MetaNames.PRODUCT): self.product,
            str(MetaNames.LOAD_PROFILE): self.load_profile,
            str(MetaNames.COMMENT): self.comment,
            str(MetaNames.DESCRIPTION): self.description,
            str(MetaNames.FILENAME): self.file_name
        }
        
        filter = FilterComposition(**filter_data)
        
        with self.tableContainer:
            self.controller.handle_measurement_table_request(filter)

    def reset_time(self):
        self.time = None
        self.update_table()
        
    def reset_date(self):
        self.date = None
        self.update_table()


    def reset(self) -> None:
        self.date = None
        self.time = None
        self.oven_nr = ""
        self.oven_Recipe = ""
        self.product = ""
        self.load_profile = ""
        self.comment = ""
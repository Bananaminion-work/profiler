from typing import Optional

from nicegui import ui
from src.shared.filter_composition import FilterComposition
from src.ui.pages.base_pages import SubPage
from src.shared.meta_names import MetaNames
from datetime import datetime


class PlotPage_selectData(SubPage):
    pageName = "plot-select"
    date: Optional[datetime] = None
    time: Optional[datetime] = None
    oven_nr: str = ""
    oven_Recipe: str = ""
    product: str = ""
    load_profile: str = ""
    comment: str = ""

    def build_content(self) -> None:
        
        with ui.column().classes("w-full gap-4"):
            
            # section 1 - filters
            with ui.card().classes("w-full"):
                with ui.grid(columns=3).classes("w-full gap-3"):
                    ui.label("Select the filters for the measurement table").classes("text-lg col-span-3")
                    ui.date("Pick the date", on_change=self.update_table).props("type=date").bind_value(self, "date")
                    ui.time("Enter the time", on_change=self.update_table).props("format24h").bind_value(self, "time")
                    ui.input("Enter the oven number", placeholder="Oven number", on_change=self.update_table).props("debounce=300").bind_value(self, "oven_nr")
                    ui.input("Enter the oven recipe", placeholder="Oven recipe", on_change=self.update_table).props("debounce=300").bind_value(self, "oven_Recipe")
                    ui.input("Enter the product name", placeholder="Product name", on_change=self.update_table).props("debounce=300").bind_value(self, "product")
                    ui.input("Enter the load profile", placeholder="Load profile", on_change=self.update_table).props("debounce=300").bind_value(self, "load_profile")
                    ui.input("Enter the comment", placeholder="Comment", on_change=self.update_table).props("debounce=300").bind_value(self, "comment")

            with ui.card().classes("w-full min-h-96"):
                self.tableContainer = ui.column().classes("w-full h-full")
                self.update_table()

            # section 3 - buttons
            with ui.row().classes("justify-end w-full"):
                ui.button(
                    "Show selected",
                    on_click=lambda: self.controller.handle_show_selected_request()
                    )
                
                ui.button(
                    "Discard",
                    color="negative",
                    on_click=lambda: self.controller.handle_popup(
                        "confirm",
                        "Are you sure to discard and return to home?",
                        self.pageName,
                    )
                )


    
    def update_table(self):
        """clears plot container and redraws with fresh plot"""
        
        #check whether the container already exists
        if not hasattr(self, "tableContainer"):
            return
        
        self.tableContainer.clear()
        
        # create filter composition object with the current filter values
        filter_data = {
            str(MetaNames.DATE): self.date,
            str(MetaNames.START_TIME): self.time,
            str(MetaNames.OVEN_NR): int(self.oven_nr) if self.oven_nr.isdigit() else 0,
            str(MetaNames.OVEN_RECIPE): self.oven_Recipe,
            str(MetaNames.PRODUCT): self.product,
            str(MetaNames.LOAD_PROFILE): self.load_profile,
            str(MetaNames.COMMENT): self.comment
        }
        
        filter = FilterComposition(**filter_data)
        
        with self.tableContainer:
            self.controller.handle_measurement_table_request(filter)


    def reset(self) -> None:
        self.date = None
        self.time = None
        self.oven_nr = ""
        self.oven_Recipe = ""
        self.product = ""
        self.load_profile = ""
        self.comment = ""
from src.ui.pages.base_pages import SubPage
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
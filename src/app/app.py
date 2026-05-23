from nicegui import ui
from src.ui.appcontroller import AppController

class App:
    def __init__(self):
        ui.page('/')(self._index)  # registriert _index als Page-Handler

    def _index(self):
        with ui.column().classes("w-full max-w-[1920px] mx-auto"):
            pageContainer = ui.column().classes("w-full min-h-[720px]")
            ui.separator()
            terminalContainer = ui.column().classes("w-full h-24 border p-2 overflow-auto")

        AppController(pageContainer, terminalContainer)
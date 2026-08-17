from nicegui import ui
from src.ui.appcontroller import AppController
from starlette.requests import Request

class UiShell:
    def __init__(self):
        ui.page('/')(self._index)  # registriert _index als Page-Handler

    def _index(self, request: Request):
        
        # get mail of session-user
        userMail = request.headers.get("x-forwarded-email", "")
        
        with ui.column().classes("w-full max-w-[1920px] mx-auto"):
            pageContainer = ui.column().classes("w-full min-h-[720px]")
            ui.separator()
            terminalContainer = ui.column().classes("w-full h-24 border p-2 overflow-auto")

        AppController(pageContainer, terminalContainer, userMail)
from nicegui import ui
from src.app.ui_shell import UiShell

#def main() -> None:
#    UiShell()  # registriert die Page einmalig
#    ui.run(host="127.0.0.1", port=8080, title="TMP Profiler")
#
#if __name__ in {"__main__", "__mp_main__"}:
#    main()


# databricks test:
controller = UiShell()

ui.run(host="0.0.0.0", port=8000, title="Temp-Profiler", reload=False)
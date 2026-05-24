from nicegui import ui
from src.app.app import App

def main() -> None:
    App()  # registriert die Page einmalig
    ui.run(host="127.0.0.1", port=8080, title="TMP Profiler")

if __name__ in {"__main__", "__mp_main__"}:
    main()
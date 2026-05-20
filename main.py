from nicegui import ui

from src.ui.appcontroller import AppController


def main() -> None:
    """Start the NiceGUI app locally for browser-based testing."""
    AppController()
    ui.run(host="127.0.0.1", port=8080, title="TMP Profiler")


if __name__ in {"__main__", "__mp_main__"}:
    main()

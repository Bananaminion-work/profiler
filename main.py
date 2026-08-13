import os

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

# databricks port
cloutPort = int(os.environ.get("PORT", 8000))

ui.run(
    host="0.0.0.0",
    port=cloutPort,
    title="Temp-Profiler",
    reload=False,
    socket_io_options={'max_http_buffer_size': 50*1024*1024}
)
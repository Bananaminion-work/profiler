import os

from nicegui import ui
from src.app.ui_shell import UiShell
from engineio.payload import Payload

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

Payload.max_decode_packets = 500

ui.run(
    host="0.0.0.0",
    port=cloutPort,
    title="Temp-Profiler",
    reload=False
)